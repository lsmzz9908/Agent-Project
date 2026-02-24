from __future__ import annotations
from src.common.types import Level, TradePlan

def build_trade_plan(entry: float, side: str, support: Level | None, resistance: Level | None, atr: float, cfg: dict) -> TradePlan:
    stop = (support.price - cfg["stop_loss"]["buffer_atr_k"] * atr) if (side=="LONG" and support) else entry - atr
    if side == "SHORT":
        stop = (resistance.price + cfg["stop_loss"]["buffer_atr_k"] * atr) if resistance else entry + atr
    r = abs(entry - stop)
    tp1 = (resistance.price if resistance else entry + r) if side=="LONG" else (support.price if support else entry - r)
    return TradePlan(stop_loss=stop, take_profit_1=tp1, trailing_atr_k=cfg["trailing"]["atr_k"], time_stop_days=cfg["time_stop"]["max_holding_days"])
