from __future__ import annotations
import json, logging
from pathlib import Path

class JsonFormatter(logging.Formatter):
    def format(self, record):
        payload={"level":record.levelname,"msg":record.getMessage(),"name":record.name}
        if hasattr(record,"extra"):
            payload.update(record.extra)
        return json.dumps(payload, ensure_ascii=False)

def setup_logger(level: str, path: str) -> logging.Logger:
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    logger=logging.getLogger("kiwoom_bot")
    logger.setLevel(level)
    logger.handlers.clear()
    fh=logging.FileHandler(path, encoding="utf-8")
    fh.setFormatter(JsonFormatter())
    sh=logging.StreamHandler()
    sh.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(message)s"))
    logger.addHandler(fh); logger.addHandler(sh)
    return logger
