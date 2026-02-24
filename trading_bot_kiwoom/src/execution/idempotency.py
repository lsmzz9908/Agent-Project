from __future__ import annotations
from ..common.utils import stable_hash

class IdempotencyService:
    def __init__(self, template:str):
        self.template=template

    def make_key(self, date, symbol, side, signal_payload):
        return self.template.format(date=date,symbol=symbol,side=side,signal_hash=stable_hash(signal_payload))
