from __future__ import annotations
from dataclasses import dataclass

@dataclass
class BrokerOrderResult:
    success: bool
    order_no: str
    message: str

class KiwoomBroker:
    def __init__(self, api, logger):
        self.api=api
        self.logger=logger

    def login(self):
        return self.api.connect()==0

    def get_accounts(self):
        return [a for a in self.api.get_login_info("ACCNO").split(";") if a]

    def send_order(self, order_req):
        rc=self.api.send_order(order_req.symbol, order_req.side.value, order_req.qty, order_req.price)
        ok = rc==0
        return BrokerOrderResult(ok, f"SIM-{order_req.idempotency_key[-6:]}", "ok" if ok else "failed")
