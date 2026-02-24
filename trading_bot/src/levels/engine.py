from __future__ import annotations
import pandas as pd
from src.common.types import Level
from .pivots import pivot_highs, pivot_lows
from .clustering import cluster_prices
from .scoring import score_level

def atr(df: pd.DataFrame, period: int = 14) -> float:
    tr = (df["high"] - df["low"]).tail(period)
    return float(tr.mean()) if len(tr) else 0.0

class LevelEngine:
    def __init__(self, cfg: dict):
        self.cfg = cfg

    def build_levels(self, df: pd.DataFrame) -> list[Level]:
        lr = self.cfg["pivot_left_right"]
        hi = pivot_highs(df, lr)
        lo = pivot_lows(df, lr)
        levels = []
        atr_v = atr(df, self.cfg["zone_width"]["atr_period"])
        zone = atr_v * self.cfg["zone_width"]["atr_k"] if self.cfg["zone_width"]["mode"] == "atr" else df["close"].iloc[-1]*self.cfg["zone_width"]["pct"]/100
        for price, touches in cluster_prices([float(df["high"].iloc[i]) for i in hi]):
            sc = score_level(touches, 1.0, 1.0, self.cfg["scoring"])
            levels.append(Level(price, "resistance", zone, touches, sc, df["ts"].iloc[-1], "pivot_high_cluster"))
        for price, touches in cluster_prices([float(df["low"].iloc[i]) for i in lo]):
            sc = score_level(touches, 1.0, 1.0, self.cfg["scoring"])
            levels.append(Level(price, "support", zone, touches, sc, df["ts"].iloc[-1], "pivot_low_cluster"))
        return [l for l in levels if l.touches >= self.cfg["min_touches"] and l.score >= self.cfg["min_score"]]
