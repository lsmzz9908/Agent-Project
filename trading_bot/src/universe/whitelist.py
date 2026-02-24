from __future__ import annotations
from datetime import datetime
from src.common.types import Symbol

class WhitelistUniverse:
    def __init__(self, symbols: list[Symbol]) -> None:
        self.symbols = symbols

    def get_universe(self, now: datetime) -> list[Symbol]:
        return list(self.symbols)
