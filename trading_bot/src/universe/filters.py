from __future__ import annotations
import pandas as pd
from src.common.types import Symbol

class UniverseFilters:
    def __init__(self, cfg: dict, logger) -> None:
        self.cfg = cfg
        self.logger = logger

    def apply(self, market: str, symbols: list[Symbol], snapshots: dict[str, pd.DataFrame]) -> list[Symbol]:
        out = []
        for s in symbols:
            df = snapshots.get(s.ticker)
            if df is None or len(df) < 20:
                continue
            px = float(df["close"].iloc[-1])
            avg_vol = float(df["volume"].tail(20).mean())
            avg_turn = float((df["close"] * df["volume"]).tail(20).mean())
            pr = self.cfg["price_range"][market]
            if not (pr["min"] <= px <= pr["max"]):
                continue
            if avg_vol < self.cfg["min_avg_volume"][market]:
                continue
            if avg_turn < self.cfg["min_avg_turnover"][market]:
                continue
            out.append(s)
        if self.cfg["spread_limit"]["enabled"]:
            self.logger.info("spread_filter_requested_but_optional")
        if self.cfg["exclude_events"]["enabled"]:
            self.logger.info("event_filter_requested_but_optional")
        return out
