from __future__ import annotations
import pandas as pd
from src.indicators.bollinger import bollinger
from src.indicators.macd import macd
from src.indicators.candles import is_bullish_reversal, is_bearish_reversal, bullish_engulf, bearish_engulf
from src.indicators.divergence import bullish_divergence, bearish_divergence

def trigger_a_long(df: pd.DataFrame, cfg: dict) -> bool:
    _, _, lower = bollinger(df["close"], cfg["period"], cfg["std"])
    last = df.iloc[-1]
    touched = last["low"] <= lower.iloc[-1]
    rev = is_bullish_reversal(last["open"], last["high"], last["low"], last["close"], cfg["reversal"]["min_body_ratio"])
    return touched and rev

def trigger_a_short(df: pd.DataFrame, cfg: dict) -> bool:
    _, upper, _ = bollinger(df["close"], cfg["period"], cfg["std"])
    last = df.iloc[-1]
    touched = last["high"] >= upper.iloc[-1]
    rev = is_bearish_reversal(last["open"], last["high"], last["low"], last["close"], cfg["reversal"]["min_body_ratio"])
    return touched and rev

def trigger_b_long(df: pd.DataFrame, rsi_s: pd.Series, cfg: dict) -> bool:
    dcfg = cfg["divergence"]
    div = bullish_divergence(df["close"], rsi_s, dcfg["pivot_left_right"], dcfg["min_separation"], dcfg["max_separation"])
    _, _, hist = macd(df["close"], 12, 26, 9)
    macd_ok = hist.iloc[-2] < 0 <= hist.iloc[-1]
    prev, last = df.iloc[-2], df.iloc[-1]
    return div and macd_ok and bullish_engulf(prev["open"], prev["close"], last["open"], last["close"])

def trigger_b_short(df: pd.DataFrame, rsi_s: pd.Series, cfg: dict) -> bool:
    dcfg = cfg["divergence"]
    div = bearish_divergence(df["close"], rsi_s, dcfg["pivot_left_right"], dcfg["min_separation"], dcfg["max_separation"])
    _, _, hist = macd(df["close"], 12, 26, 9)
    macd_ok = hist.iloc[-2] > 0 >= hist.iloc[-1]
    prev, last = df.iloc[-2], df.iloc[-1]
    return div and macd_ok and bearish_engulf(prev["open"], prev["close"], last["open"], last["close"])
