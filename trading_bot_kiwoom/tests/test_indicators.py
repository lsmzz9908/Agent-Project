from src.indicators.rsi import rsi
from src.indicators.macd import macd

def test_rsi_range():
    s=list(range(1,80))
    out=rsi(s)
    assert all(0 <= x <= 100 for x in out)

def test_macd_len():
    s=list(range(1,80))
    line,sig,h=macd(s)
    assert len(line)==len(sig)==len(h)==len(s)
