from __future__ import annotations

import argparse

from .notify.telegram_notifier import TelegramNotifier
from .service.trading_service import TradingService, load_config


def run(config_path, run_mode_override=None, market_mode_override=None, smoke_notify=False):
    cfg = load_config(config_path)
    if run_mode_override:
        cfg["app"]["run_mode"] = run_mode_override
    if market_mode_override:
        cfg["app"]["market_mode"] = market_mode_override

    tcfg = cfg.get("telegram", {})
    notifier = TelegramNotifier(
        enabled=tcfg.get("enabled", False),
        throttle_seconds=tcfg.get("throttle_seconds", 2),
    )
    service = TradingService(cfg, notifier=notifier)

    if smoke_notify:
        service.smoke_notify()
        service.logger.info("smoke_notify_sent")
        return

    run_mode = cfg["app"]["run_mode"]
    symbols = service.get_default_universe()

    if run_mode == "backtest":
        service.logger.info("backtest_start")
        summary = service.start_swing_batch(symbols, live=False)
        service.logger.info("backtest_done", extra={"extra": summary.__dict__})
        return

    if run_mode in {"paper", "live"}:
        live = run_mode == "live"
        summary = service.start_swing_batch(symbols, live=live)
        service.logger.info("batch_done", extra={"extra": summary.__dict__})
        if live:
            service.stop()
        return

    raise RuntimeError(f"unsupported run_mode={run_mode}")


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
