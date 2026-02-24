from __future__ import annotations
import pandas as pd
from src.common.types import Signal, Symbol
from src.indicators.rsi import rsi
from src.indicators.bollinger import bollinger
from src.indicators.macd import macd
from src.levels.engine import LevelEngine, atr
from src.strategy.triggers import trigger_a_long, trigger_a_short, trigger_b_long, trigger_b_short
from src.risk.exits import build_trade_plan

class ComboSRSRsiSwingStrategy:
    def __init__(self, cfg: dict):
        self.cfg = cfg
        self.level_engine = LevelEngine(cfg["levels"])

    def _rsi_center_noisy(self, rsi_s: pd.Series) -> bool:
        low, high = self.cfg["rsi_filter"]["center_band"]
        lb = self.cfg["rsi_filter"]["center_lookback"]
        ratio = ((rsi_s.tail(lb) >= low) & (rsi_s.tail(lb) <= high)).mean()
        return ratio > self.cfg["rsi_filter"]["center_max_ratio"]

    def evaluate(self, symbol: Symbol, df: pd.DataFrame) -> Signal | None:
        levels = self.level_engine.build_levels(df)
        if not levels:
            return None
        close = float(df["close"].iloc[-1])
        candidates = [l for l in levels if abs(close - l.price) <= l.zone_width]
        if not candidates:
            return None
        rsi_s = rsi(df["close"], self.cfg["indicators"]["rsi"]["period"])
        if self._rsi_center_noisy(rsi_s):
            return None
        side = None
        trigger_used = None
        if rsi_s.iloc[-1] <= self.cfg["rsi_filter"]["long_max"]:
            if trigger_a_long(df, {**self.cfg["indicators"]["bollinger"], "reversal": self.cfg["triggers"]["A_reversal_bb"]["reversal"]}):
                side, trigger_used = "LONG", "A"
            elif trigger_b_long(df, rsi_s, self.cfg["triggers"]["B_div_macd"]):
                side, trigger_used = "LONG", "B"
        elif rsi_s.iloc[-1] >= self.cfg["rsi_filter"]["short_min"]:
            if trigger_a_short(df, {**self.cfg["indicators"]["bollinger"], "reversal": self.cfg["triggers"]["A_reversal_bb"]["reversal"]}):
                side, trigger_used = "SHORT", "A"
            elif trigger_b_short(df, rsi_s, self.cfg["triggers"]["B_div_macd"]):
                side, trigger_used = "SHORT", "B"
        if side is None:
            return None
        supports = sorted([l for l in levels if l.kind=="support"], key=lambda x: abs(x.price-close))
        ress = sorted([l for l in levels if l.kind=="resistance"], key=lambda x: abs(x.price-close))
        support = supports[0] if supports else None
        resistance = ress[0] if ress else None
        tp_cfg = self.cfg["risk"]["exits"]
        trade_plan = build_trade_plan(close, side, support, resistance, atr(df), tp_cfg)
        _, bb_u, bb_l = bollinger(df["close"], **self.cfg["indicators"]["bollinger"])
        macd_line, macd_sig, macd_hist = macd(df["close"], **self.cfg["indicators"]["macd"])
        return Signal(symbol=symbol, ts=df["ts"].iloc[-1], side=side, reason="level+rsi+trigger", trigger=trigger_used,
            indicators={"rsi": float(rsi_s.iloc[-1]), "bb_u": float(bb_u.iloc[-1]), "bb_l": float(bb_l.iloc[-1]), "macd": float(macd_line.iloc[-1]), "macd_sig": float(macd_sig.iloc[-1]), "macd_hist": float(macd_hist.iloc[-1])},
            levels=levels, trade_plan=trade_plan)
