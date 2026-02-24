from __future__ import annotations

import argparse
from datetime import datetime
from pathlib import Path

from src.common.logger import build_logger
from src.common.timecal import MarketCalendar
from src.common.utils import load_config
from src.execution.broker_shinhan import ShinhanBroker
from src.execution.order_manager import OrderManager
from src.storage.db import Database
from src.storage.repo import Repo
from src.strategy.combo_sr_rsi_swing import ComboSRSRsiSwingStrategy


def _resolve_runtime_path(config_path: str, maybe_relative: str) -> str:
    candidate = Path(maybe_relative)
    if candidate.is_absolute():
        return str(candidate)
    project_root = Path(config_path).resolve().parent.parent
    return str((project_root / candidate).resolve())


def run_backtest(cfg, logger):
    logger.info("backtest_mode_ready")


def run_paper(cfg, logger):
    logger.info("paper_mode_ready")


def run_live(cfg, logger):
    broker = ShinhanBroker()
    OrderManager(broker, logger)
    cal = MarketCalendar()
    now = datetime.utcnow()
    for market in (["KR", "US"] if cfg["app"]["market_mode"] == "BOTH" else (["KR"] if cfg["app"]["market_mode"] == "KR" else ["US"])):
        if cal.is_open(market, now, cfg["app"]["timezone"][market]):
            logger.info("market_loop_live", extra={"market": market})


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--config", required=True)
    args = p.parse_args()
    cfg = load_config(args.config)

    log_path = _resolve_runtime_path(args.config, cfg["logging"]["log_path"])
    db_path = _resolve_runtime_path(args.config, cfg["storage"]["db_path"])

    logger = build_logger(cfg["app"]["name"], cfg["logging"]["level"], log_path)

    db = Database(db_path)
    db.init()
    Repo(db)
    ComboSRSRsiSwingStrategy(cfg)

    mode = cfg["app"]["run_mode"]
    if mode == "backtest":
        run_backtest(cfg["backtest"], logger)
    elif mode == "paper":
        run_paper(cfg, logger)
    elif mode == "live":
        run_live(cfg, logger)
    else:
        raise ValueError(f"unknown run mode: {mode}")


if __name__ == "__main__":
    main()
