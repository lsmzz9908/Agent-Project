from __future__ import annotations
from dataclasses import dataclass


@dataclass
class BrokerOrderResult:
    success: bool
    order_no: str
    message: str


class KiwoomBroker:
    def __init__(self, api, logger):
        self.api = api
        self.logger = logger
        self.account_no: str | None = None

    def login(self):
        self.api.connect_and_login()
        accounts = self.get_accounts()
        if not accounts:
            self.logger.error("account_list_empty")
            raise RuntimeError("No account from GetLoginInfo('ACCNO').")
        self.account_no = accounts[0]
        return True

    def get_accounts(self):
        return [a for a in self.api.get_login_info("ACCNO").split(";") if a]

    def send_order(self, order_req):
        if not self.account_no:
            raise RuntimeError("Broker is not logged in.")

        order_type = 1 if order_req.side.value == "BUY" else 2
        price = int(order_req.price or 0)
        hoga = "03" if price == 0 else "00"
        rc = self.api.send_order(
            rqname=f"ORDER_{order_req.idempotency_key[-8:]}",
            screen_no="2000",
            acc_no=self.account_no,
            order_type=order_type,
            code=order_req.symbol,
            qty=int(order_req.qty),
            price=price,
            hoga=hoga,
            org_order_no="",
        )
        ok = rc == 0
        return BrokerOrderResult(ok, f"ORD-{order_req.idempotency_key[-6:]}", "ok" if ok else f"failed:{rc}")
