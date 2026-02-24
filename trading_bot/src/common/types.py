from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Literal

Market = Literal["KR", "US"]
Side = Literal["LONG", "SHORT"]

@dataclass
class Symbol:
    market: Market
    ticker: str
    exchange: str
    currency: str
    timezone: str

@dataclass
class Candle:
    ts: datetime
    open: float
    high: float
    low: float
    close: float
    volume: float

@dataclass
class Level:
    price: float
    kind: Literal["support", "resistance"]
    zone_width: float
    touches: int
    score: float
    last_touch_ts: datetime
    source: str

@dataclass
class TradePlan:
    stop_loss: float
    take_profit_1: float
    trailing_atr_k: float
    time_stop_days: int
    metadata: dict[str, Any] = field(default_factory=dict)

@dataclass
class Signal:
    symbol: Symbol
    ts: datetime
    side: Side
    reason: str
    trigger: str
    indicators: dict[str, Any]
    levels: list[Level]
    trade_plan: TradePlan

@dataclass
class Position:
    symbol: Symbol
    side: Side
    qty: float
    entry_price: float
    stop_loss: float
    take_profit_1: float
    trailing_stop: float | None
    opened_at: datetime
    max_holding_days: int
