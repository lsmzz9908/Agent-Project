import pandas as pd
from src.strategy.combo_sr_rsi_swing import ComboSRSRsiSwingStrategy
from src.common.types import Symbol


def test_strategy_signal_or_none():
    rows=[]
    price=100
    for i in range(220):
        price += (-1 if i%11==0 else 0.4)
        rows.append({"ts": pd.Timestamp("2023-01-01") + pd.Timedelta(days=i), "open": price-1, "high": price+2, "low": price-3, "close": price, "volume": 500000})
    df = pd.DataFrame(rows)
    from src.common.utils import load_config
    cfg = load_config("config/config.yml")
    s = Symbol("KR","005930","KRX","KRW","Asia/Seoul")
    strategy = ComboSRSRsiSwingStrategy(cfg)
    signal = strategy.evaluate(s, df)
    assert signal is None or signal.trade_plan.time_stop_days == cfg["risk"]["exits"]["time_stop"]["max_holding_days"]
