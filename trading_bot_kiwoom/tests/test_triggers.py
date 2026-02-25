from src.strategy.triggers import trigger_div_macd

def test_trigger_div_macd():
    assert trigger_div_macd(True,-1,1)
    assert not trigger_div_macd(False,-1,1)
