from __future__ import annotations

import argparse
import platform
from pathlib import Path

from .backtest.engine import BacktestEngine
from .common.logger import setup_logger
from .data.marketdata import MarketDataService
from .execution.idempotency import IdempotencyService
from .execution.order_manager import OrderManager
from .kiwoom.broker_kiwoom import KiwoomBroker
from .kiwoom.kiwoom_api import KiwoomAPI
from .notify.telegram_notifier import TelegramNotifier
from .storage.repo import Repository
from .strategy.combo_sr_rsi_swing import ComboSRSRsiSwing
from .universe.hybrid import HybridUniverse


def _load_config(path):
    try:
        import yaml

        return yaml.safe_load(open(path, encoding="utf-8"))
    except Exception:
        text = Path(path).read_text(encoding="utf-8")
        run_mode = "paper"
        if 'run_mode: "backtest"' in text:
            run_mode = "backtest"
        if 'run_mode: "live"' in text:
            run_mode = "live"
        return {
            "app": {"run_mode": run_mode, "market_mode": "KR"},
            "logging": {"level": "INFO", "log_path": "logs/bot.jsonl", "heartbeat_log": True},
            "storage": {"db_path": "data/trading.db"},
            "universe": {"whitelist_symbols": ["005930", "000660"]},
            "idempotency": {"key_template": "{date}:{symbol}:{side}:{signal_hash}"},
            "telegram": {"enabled": False, "daily_summary_time": "15:50", "throttle_seconds": 2},
        }


def run(config_path, run_mode_override=None, market_mode_override=None, smoke_notify=False):
    cfg = _load_config(config_path)
    if run_mode_override:
        cfg["app"]["run_mode"] = run_mode_override
    if market_mode_override:
        cfg["app"]["market_mode"] = market_mode_override

    logger = setup_logger(cfg["logging"]["level"], cfg["logging"]["log_path"])
    telegram_cfg = cfg.get("telegram", {})
    notifier = TelegramNotifier(
        enabled=telegram_cfg.get("enabled", False),
        throttle_seconds=telegram_cfg.get("throttle_seconds", 2),
        logger=logger,
    )

    if smoke_notify:
        notifier.send("📢 알림 테스트")
        logger.info("smoke_notify_sent")
        return

    repo = Repository(cfg["storage"]["db_path"])
    symbols = HybridUniverse(cfg["universe"]["whitelist_symbols"]).get_symbols()
    strategy = ComboSRSRsiSwing()
    mds = MarketDataService()

    run_mode = cfg["app"]["run_mode"]
    logger.info("heartbeat", extra={"extra": {"universe_count": len(symbols), "run_mode": run_mode}})

    if run_mode == "backtest":
        sigs = BacktestEngine().run(symbols, strategy, mds)
        logger.info("backtest_done", extra={"extra": {"signals_found": len(sigs)}})
        return

    api = KiwoomAPI(logger)
    broker = KiwoomBroker(api, logger)
    idem = IdempotencyService(cfg["idempotency"]["key_template"])
    om = OrderManager(repo, broker, idem, logger, notifier=notifier)
    api.register_callback("chejan", om.handle_chejan)

    try:
        if run_mode == "live":
            if platform.system() != "Windows":
                logger.error("live_mode_windows_only", extra={"extra": {"detected_os": platform.system()}})
                raise RuntimeError(f"live mode supports only Windows. detected_os={platform.system()}")
            broker.login()  # connect_and_login() + account load/validation
            notifier.send("🟢 키움 로그인 성공")

        trades = 0
        for s in symbols:
            sig = strategy.evaluate(s, mds.get_daily(s))
            if sig:
                repo.insert_signal(sig)
                if run_mode == "live":
                    om.place_entry(sig, qty=1)
                trades += 1

        if trades == 0 and cfg["logging"].get("heartbeat_log", True):
            logger.info("no_trade_today", extra={"extra": {"evaluated_symbols": len(symbols), "signals_found": 0}})
    finally:
        notifier.send("⚪ 프로그램 종료")
        api.close()


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--config", required=True)
    p.add_argument("--run_mode")
    p.add_argument("--market_mode")
    p.add_argument("--smoke_notify", action="store_true")
    args = p.parse_args()
    run(args.config, args.run_mode, args.market_mode, args.smoke_notify)


if __name__ == "__main__":
    main()
