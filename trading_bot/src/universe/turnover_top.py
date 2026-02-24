from __future__ import annotations
from datetime import datetime
from src.common.types import Symbol

class TurnoverTopUniverse:
    def __init__(self, scanner, top_n: int, lookback_days: int = 20) -> None:
        self.scanner = scanner
        self.top_n = top_n
        self.lookback_days = lookback_days

    def get_universe(self, now: datetime) -> list[Symbol]:
        return self.scanner.scan_turnover_top(self.top_n, self.lookback_days)
