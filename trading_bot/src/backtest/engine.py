from __future__ import annotations
from src.backtest.metrics import compute_metrics

class BacktestEngine:
    def __init__(self, strategy, cfg: dict):
        self.strategy = strategy
        self.cfg = cfg

    def run(self, symbol, df):
        trades = []
        for i in range(100, len(df)-1):
            window = df.iloc[:i+1]
            sig = self.strategy.evaluate(symbol, window)
            if not sig:
                continue
            entry = float(df["open"].iloc[i+1]) * (1 + self.cfg["slippage_pct"]/100)
            exit_px = float(df["close"].iloc[min(i+5, len(df)-1)])
            pnl = (exit_px - entry) if sig.side == "LONG" else (entry - exit_px)
            fee = entry * self.cfg["fee_rate"]
            trades.append({"pnl": pnl - fee, "r": (pnl / max(abs(entry - sig.trade_plan.stop_loss),1e-9))})
        return compute_metrics(trades)
