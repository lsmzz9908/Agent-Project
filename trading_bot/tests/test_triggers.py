import pandas as pd
from src.strategy.triggers import trigger_a_long


def test_trigger_a_long_true():
    vals = [100]*25
    vals[-1] = 90
    df = pd.DataFrame({
        "open": vals,
        "high": [v+2 for v in vals],
        "low": [v-5 for v in vals],
        "close": [v+1 for v in vals],
    })
    cfg={"period":20,"std":2,"reversal":{"min_body_ratio":0.1}}
    assert trigger_a_long(df,cfg)
