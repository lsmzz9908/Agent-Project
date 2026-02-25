from __future__ import annotations
from .history import load_sample_ohlcv

class MarketDataService:
    def get_daily(self, symbol:str, bars:int=120):
        return load_sample_ohlcv(symbol,bars)
