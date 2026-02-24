from __future__ import annotations
from .base import Strategy
from .triggers import trigger_div_macd
from ..common.types import Signal, Side
from ..common.utils import make_signal_id
from ..indicators.rsi import rsi
from ..indicators.macd import macd

class ComboSRSRsiSwing(Strategy):
    def evaluate(self, symbol, rows):
        close=[r['close'] for r in rows]
        r = rsi(close)[-1]
        _,_,h = macd(close)
        if len(h) >= 2 and r <= 45 and trigger_div_macd(True, h[-2], h[-1]):
            return Signal(make_signal_id(), symbol, Side.BUY, 0.9, "RSI+MACD trigger")
        return None
