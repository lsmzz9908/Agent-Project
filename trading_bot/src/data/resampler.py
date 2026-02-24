from __future__ import annotations
import pandas as pd

def resample_ohlcv(df: pd.DataFrame, rule: str) -> pd.DataFrame:
    out = df.set_index("ts").resample(rule).agg({
        "open": "first", "high": "max", "low": "min", "close": "last", "volume": "sum"
    }).dropna().reset_index()
    return out
