from __future__ import annotations
import pandas as pd

def bollinger(close: pd.Series, period: int = 20, std: float = 2.0):
    ma = close.rolling(period).mean()
    sd = close.rolling(period).std(ddof=0)
    return ma, ma + std*sd, ma - std*sd
