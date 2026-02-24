from __future__ import annotations
import pandas as pd
from src.levels.pivots import pivot_lows, pivot_highs

def bullish_divergence(close: pd.Series, rsi: pd.Series, lr: int, min_sep: int, max_sep: int) -> bool:
    piv = pivot_lows(pd.DataFrame({"low": close, "high": close}), lr)
    if len(piv) < 2:
        return False
    a,b = piv[-2], piv[-1]
    sep = b-a
    return min_sep <= sep <= max_sep and close.iloc[b] < close.iloc[a] and rsi.iloc[b] > rsi.iloc[a]

def bearish_divergence(close: pd.Series, rsi: pd.Series, lr: int, min_sep: int, max_sep: int) -> bool:
    piv = pivot_highs(pd.DataFrame({"high": close, "low": close}), lr)
    if len(piv) < 2:
        return False
    a,b = piv[-2], piv[-1]
    sep = b-a
    return min_sep <= sep <= max_sep and close.iloc[b] > close.iloc[a] and rsi.iloc[b] < rsi.iloc[a]
