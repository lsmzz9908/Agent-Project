from __future__ import annotations
import logging
from pythonjsonlogger import jsonlogger
from .utils import ensure_parent

def build_logger(name: str, level: str, log_path: str) -> logging.Logger:
    ensure_parent(log_path)
    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.handlers.clear()

    fmt = jsonlogger.JsonFormatter('%(asctime)s %(levelname)s %(name)s %(message)s')
    fh = logging.FileHandler(log_path)
    fh.setFormatter(fmt)
    sh = logging.StreamHandler()
    sh.setFormatter(fmt)
    logger.addHandler(fh)
    logger.addHandler(sh)
    return logger
