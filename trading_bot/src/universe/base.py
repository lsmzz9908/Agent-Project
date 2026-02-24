from __future__ import annotations
from datetime import datetime
from typing import Protocol
from src.common.types import Symbol

class UniverseProvider(Protocol):
    def get_universe(self, now: datetime) -> list[Symbol]: ...
