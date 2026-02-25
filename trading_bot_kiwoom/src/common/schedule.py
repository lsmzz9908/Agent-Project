from __future__ import annotations
from dataclasses import dataclass

@dataclass
class SchedulePlan:
    universe_refresh_time: str
    evaluate_time: str
    order_execute_time: str
