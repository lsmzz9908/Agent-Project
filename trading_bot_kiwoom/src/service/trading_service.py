from __future__ import annotations

import platform
import threading
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Callable

from ..common.logger import setup_logger
from ..data.marketdata import MarketDataService
from ..execution.idempotency import IdempotencyService
from ..execution.order_manager import OrderManager
from ..kiwoom.broker_kiwoom import KiwoomBroker
from ..kiwoom.kiwoom_api import KiwoomAPI
from ..notify.telegram_notifier import TelegramNotifier
from ..storage.repo import Repository
from ..strategy.combo_sr_rsi_swing import ComboSRSRsiSwing
from ..universe.hybrid import HybridUniverse


@dataclass
class RunSummary:
    evaluated_symbols: int = 0
    signals_found: int = 0
    orders_sent: int = 0
    fills: int = 0
    last_eval_time: str | None = None
    last_order_time: str | None = None
    last_fill_time: str | None = None


class TradingService:
    def __init__(self, config: dict, logger=None, status_cb: Callable[[str], None] | None = None):
        self.cfg = config
        self.logger = logger or setup_logger(config["logging"]["level"], config["logging"]["log_path"])
        self.status_cb = status_cb or (lambda _msg: None)

        tcfg = config.get("telegram", {})
        self.notifier = TelegramNotifier(
            enabled=tcfg.get("enabled", False),
            throttle_seconds=tcfg.get("throttle_seconds", 2),
            logger=self.logger,
        )

        self.repo = Repository(config["storage"]["db_path"])
        self.mds = MarketDataService()
        self.strategy = ComboSRSRsiSwing()
        self.idem = IdempotencyService(config["idempotency"]["key_template"])

        self.api = None
        self.broker = None
        self.om = None

        self._realtime_thread: threading.Thread | None = None
        self._stop_event = threading.Event()
        self.summary = RunSummary()
        self.current_mode = "IDLE"

    def _status(self, msg: str):
        self.logger.info(msg)
        self.status_cb(msg)

    def _mask_account(self, acc: str) -> str:
        if len(acc) < 4:
            return "****"
        return f"{acc[:2]}****{acc[-2:]}"

    def _ensure_live_stack(self):
        if platform.system() != "Windows":
            self.notifier.send("🔴 로그인 실패: Windows 환경이 아닙니다")
            raise RuntimeError(f"live mode supports only Windows. detected_os={platform.system()}")

        if self.api is None:
            self.api = KiwoomAPI(self.logger)
            self.broker = KiwoomBroker(self.api, self.logger)
            self.om = OrderManager(self.repo, self.broker, self.idem, self.logger, notifier=self.notifier)
            self.api.register_callback("chejan", self._on_chejan)

    def _on_chejan(self, payload: dict):
        self.summary.last_fill_time = datetime.now().strftime("%H:%M:%S")
        self.summary.fills += 1
        if self.om:
            self.om.handle_chejan(payload)

    def _login(self):
        self._ensure_live_stack()
        self._status("login_start")
        try:
            self.broker.login()
            masked = self._mask_account(self.broker.account_no or "")
            self._status(f"login_success account={masked}")
            self.notifier.send("🟢 키움 로그인 성공")
        except Exception as exc:
            self.notifier.send(f"🔴 로그인 실패: {type(exc).__name__}")
            raise

    def stop(self):
        self._status("stopping")
        self._stop_event.set()
        if self._realtime_thread and self._realtime_thread.is_alive():
            self._realtime_thread.join(timeout=3)
        if self.api:
            self.api.close()
            self.api = None
        self.current_mode = "STOPPED"
        self._status("stopped")
        self.notifier.send("⚪ 프로그램 종료")

    def get_default_universe(self) -> list[str]:
        symbols = HybridUniverse(self.cfg["universe"]["whitelist_symbols"]).get_symbols()
        if symbols:
            return symbols
        return self.load_universe_csv("data/universe_kospi200.csv")

    def load_universe_csv(self, path: str) -> list[str]:
        p = Path(path)
        if not p.exists():
            return []
        out: list[str] = []
        for raw in p.read_text(encoding="utf-8").splitlines():
            line = raw.strip()
            if not line:
                continue
            first = line.split(",", 1)[0].strip().replace("\ufeff", "")
            if first.lower() in {"symbol", "code", "종목코드"}:
                continue
            code = "".join(ch for ch in first if ch.isdigit())
            if len(code) == 6:
                out.append(code)
        return sorted(set(out))

    def load_custom_universe(self, path: str = "data/universe/custom.txt") -> list[str]:
        p = Path(path)
        if not p.exists():
            return []
        out = []
        for raw in p.read_text(encoding="utf-8").splitlines():
            code = "".join(ch for ch in raw.strip() if ch.isdigit())
            if len(code) == 6:
                out.append(code)
        return sorted(set(out))

    def save_custom_universe(self, symbols: list[str], path: str = "data/universe/custom.txt"):
        p = Path(path)
        p.parent.mkdir(parents=True, exist_ok=True)
        normalized = sorted({"".join(ch for ch in s if ch.isdigit()) for s in symbols if len("".join(ch for ch in s if ch.isdigit())) == 6})
        p.write_text("\n".join(normalized) + "\n", encoding="utf-8")

    def _evaluate_once(self, universe: list[str], send_orders: bool) -> RunSummary:
        summary = RunSummary(evaluated_symbols=len(universe), last_eval_time=datetime.now().strftime("%H:%M:%S"))
        for s in universe:
            if self._stop_event.is_set():
                break
            sig = self.strategy.evaluate(s, self.mds.get_daily(s))
            if not sig:
                continue
            summary.signals_found += 1
            self.repo.insert_signal(sig)
            if send_orders and self.om:
                oid = self.om.place_entry(sig, qty=1)
                if oid is not None:
                    summary.orders_sent += 1
                    summary.last_order_time = datetime.now().strftime("%H:%M:%S")

        self.summary = summary
        if summary.signals_found == 0:
            self._status("no_trade_today")
        self._status(
            f"run_summary evaluated={summary.evaluated_symbols} signals={summary.signals_found} orders={summary.orders_sent}"
        )
        return summary

    def start_swing_batch(self, universe: list[str], live: bool = True) -> RunSummary:
        self.current_mode = "SWING"
        self._stop_event.clear()
        if live:
            self._login()
        return self._evaluate_once(universe, send_orders=live)

    def start_realtime(self, universe: list[str], interval_seconds: int = 60, live: bool = True):
        self.current_mode = "REALTIME"
        self._stop_event.clear()
        if live:
            self._login()

        def _loop():
            self._status(f"realtime_started interval={interval_seconds}s universe={len(universe)}")
            while not self._stop_event.is_set():
                try:
                    self._evaluate_once(universe, send_orders=live)
                    self._status("realtime_heartbeat")
                except Exception as exc:
                    self._status(f"realtime_error={type(exc).__name__}")
                    self.notifier.send(f"🔴 오류 발생: {type(exc).__name__}")
                self._stop_event.wait(interval_seconds)

        self._realtime_thread = threading.Thread(target=_loop, daemon=True)
        self._realtime_thread.start()

    def smoke_notify(self):
        self.notifier.send("📢 알림 테스트")


def load_config(path: str) -> dict:
    try:
        import yaml

        return yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    except Exception:
        text = Path(path).read_text(encoding="utf-8")
        run_mode = "paper"
        if 'run_mode: "live"' in text:
            run_mode = "live"
        return {
            "app": {"run_mode": run_mode, "market_mode": "KR"},
            "logging": {"level": "INFO", "log_path": "logs/bot.jsonl", "heartbeat_log": True},
            "storage": {"db_path": "data/trading.db"},
            "universe": {"whitelist_symbols": ["005930", "000660"]},
            "idempotency": {"key_template": "{date}:{symbol}:{side}:{signal_hash}"},
            "telegram": {"enabled": False, "daily_summary_time": "15:50", "throttle_seconds": 2},
            "realtime": {"enabled": True, "interval_seconds": 300},
        }
