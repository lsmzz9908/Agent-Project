from __future__ import annotations

def risk_based_size(balance: float, risk_per_trade: float, entry: float, stop: float) -> float:
    risk_cash = balance * risk_per_trade
    per_share = max(abs(entry - stop), 1e-9)
    return max(risk_cash / per_share, 0)
