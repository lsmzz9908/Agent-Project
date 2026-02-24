from __future__ import annotations
import json
from pathlib import Path
from typing import Any
import yaml

def load_config(path: str) -> dict[str, Any]:
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

def ensure_parent(path: str) -> None:
    Path(path).parent.mkdir(parents=True, exist_ok=True)

def to_json(data: dict[str, Any]) -> str:
    return json.dumps(data, ensure_ascii=False, default=str)
