import pandas as pd
from src.levels.engine import LevelEngine


def test_level_engine_builds_levels():
    rows=[]
    for i in range(120):
        base = 100 + (i%20)
        rows.append({"ts": pd.Timestamp("2024-01-01") + pd.Timedelta(days=i), "open": base, "high": base+2, "low": base-2, "close": base+1, "volume": 100000})
    df = pd.DataFrame(rows)
    cfg = {
        "pivot_left_right": 3,
        "zone_width": {"mode": "atr", "atr_period": 14, "atr_k": 0.6, "pct": 0.5},
        "min_touches": 1,
        "min_score": 0,
        "scoring": {"w_touches": 0.5, "w_reaction": 0.3, "w_recency": 0.2},
    }
    levels = LevelEngine(cfg).build_levels(df)
    assert len(levels) > 0
