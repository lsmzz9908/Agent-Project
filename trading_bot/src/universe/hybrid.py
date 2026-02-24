from __future__ import annotations
from datetime import datetime

class HybridUniverse:
    def __init__(self, whitelist, turnover, filters, snapshots_provider):
        self.whitelist = whitelist
        self.turnover = turnover
        self.filters = filters
        self.snapshots_provider = snapshots_provider

    def get_universe(self, now: datetime):
        raw = {s.ticker: s for s in self.whitelist.get_universe(now)}
        raw.update({s.ticker: s for s in self.turnover.get_universe(now)})
        syms = list(raw.values())
        market = syms[0].market if syms else "KR"
        return self.filters.apply(market, syms, self.snapshots_provider(syms))
