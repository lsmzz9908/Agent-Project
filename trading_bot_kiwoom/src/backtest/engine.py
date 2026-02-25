class BacktestEngine:
    def run(self, symbols, strategy, mds):
        signals=[]
        for s in symbols:
            sig=strategy.evaluate(s, mds.get_daily(s))
            if sig: signals.append(sig)
        return signals
