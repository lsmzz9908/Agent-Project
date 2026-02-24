from src.strategy.combo_sr_rsi_swing import ComboSRSRsiSwing
from src.data.history import load_sample_ohlcv

def test_strategy_returns_optional_signal():
    sig=ComboSRSRsiSwing().evaluate('005930', load_sample_ohlcv('005930',120))
    assert sig is None or sig.symbol=='005930'
