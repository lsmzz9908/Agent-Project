from __future__ import annotations
from datetime import datetime
from zoneinfo import ZoneInfo

class MarketCalendar:
    def __init__(self) -> None:
        self.hours = {
            "KR": (9, 15),
            "US": (9, 16),
        }

    def is_open(self, market: str, now: datetime, tz_name: str) -> bool:
        local = now.astimezone(ZoneInfo(tz_name))
        if local.weekday() >= 5:
            return False
        start_h, end_h = self.hours[market]
        return start_h <= local.hour < end_h
