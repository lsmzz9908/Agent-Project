from __future__ import annotations
from typing import Protocol
import pandas as pd
from src.common.types import Symbol

class DataFeed(Protocol):
    def get_daily_ohlcv(self, symbol: Symbol, lookback: int = 500) -> pd.DataFrame: ...

class BrokerDataFeed:
    def __init__(self, broker) -> None:
        self.broker = broker

    def get_daily_ohlcv(self, symbol: Symbol, lookback: int = 500) -> pd.DataFrame:
        return self.broker.get_daily_ohlcv(symbol, lookback)
