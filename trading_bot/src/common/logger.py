from __future__ import annotations

import json
import logging
from datetime import datetime

from .utils import ensure_parent


class JsonLineFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        payload = {
            "ts": datetime.utcfromtimestamp(record.created).isoformat() + "Z",
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        if hasattr(record, "market"):
            payload["market"] = record.market
        if hasattr(record, "symbol"):
            payload["symbol"] = record.symbol
        if hasattr(record, "timeframe"):
            payload["timeframe"] = record.timeframe
        return json.dumps(payload, ensure_ascii=False)


def build_logger(name: str, level: str, log_path: str) -> logging.Logger:
    ensure_parent(log_path)
    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.handlers.clear()

    formatter = JsonLineFormatter()
    fh = logging.FileHandler(log_path)
    fh.setFormatter(formatter)

    sh = logging.StreamHandler()
    sh.setFormatter(formatter)

    logger.addHandler(fh)
    logger.addHandler(sh)
    return logger
