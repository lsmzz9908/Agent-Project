import pandas as pd
from src.indicators.rsi import rsi
from src.indicators.bollinger import bollinger
from src.indicators.macd import macd


def test_rsi_range():
    s = pd.Series([i + (i%3) for i in range(1, 80)])
    out = rsi(s, 14).dropna()
    assert ((out >= 0) & (out <= 100)).all()


def test_bollinger_order():
    s = pd.Series(range(1, 60))
    ma, up, lo = bollinger(s, 20, 2)
    assert up.iloc[-1] > ma.iloc[-1] > lo.iloc[-1]


def test_macd_hist_exists():
    s = pd.Series(range(1, 100))
    _, _, h = macd(s)
    assert h.notna().sum() > 0
