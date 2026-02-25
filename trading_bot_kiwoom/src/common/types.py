from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

class Side(str, Enum):
    BUY = "BUY"
    SELL = "SELL"

@dataclass
class Signal:
    signal_id: str
    symbol: str
    side: Side
    score: float
    reason: str
    meta: dict[str, Any] = field(default_factory=dict)

@dataclass
class OrderRequest:
    symbol: str
    side: Side
    qty: int
    price: float | None
    signal_id: str
    idempotency_key: str
