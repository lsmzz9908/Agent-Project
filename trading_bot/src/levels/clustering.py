from __future__ import annotations

def cluster_prices(prices: list[float], threshold_pct: float = 0.6) -> list[tuple[float,int]]:
    if not prices:
        return []
    prices = sorted(prices)
    clusters = [[prices[0]]]
    for p in prices[1:]:
        c = clusters[-1]
        center = sum(c)/len(c)
        if abs(p-center)/center*100 <= threshold_pct:
            c.append(p)
        else:
            clusters.append([p])
    return [(sum(c)/len(c), len(c)) for c in clusters]
