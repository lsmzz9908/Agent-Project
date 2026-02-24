from __future__ import annotations

def can_open_more(current_positions: int, max_positions: int) -> bool:
    return current_positions < max_positions

def hit_daily_loss_limit(pnl_ratio_today: float, daily_loss_limit: float) -> bool:
    return pnl_ratio_today <= -abs(daily_loss_limit)
