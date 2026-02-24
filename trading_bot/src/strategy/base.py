from __future__ import annotations
from typing import Protocol
from src.common.types import Signal, Symbol
import pandas as pd

class Strategy(Protocol):
    def evaluate(self, symbol: Symbol, df: pd.DataFrame) -> Signal | None: ...
