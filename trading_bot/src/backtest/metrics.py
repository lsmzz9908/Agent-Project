from __future__ import annotations

def compute_metrics(trades: list[dict]) -> dict:
    if not trades:
        return {"total_pnl": 0, "win_rate": 0, "pf": 0, "mdd": 0, "avg_r": 0}
    pnls = [t["pnl"] for t in trades]
    wins = [p for p in pnls if p > 0]
    losses = [-p for p in pnls if p < 0]
    pf = (sum(wins) / sum(losses)) if losses else float("inf")
    equity = 0
    peak = 0
    mdd = 0
    for p in pnls:
        equity += p
        peak = max(peak, equity)
        mdd = min(mdd, equity - peak)
    return {"total_pnl": sum(pnls), "win_rate": len(wins)/len(pnls), "pf": pf, "mdd": mdd, "avg_r": sum(t.get("r",0) for t in trades)/len(trades)}
