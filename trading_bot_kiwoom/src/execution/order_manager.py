from __future__ import annotations
import datetime as dt
from .state_machine import OrderState, next_order_state

class OrderManager:
    def __init__(self, repo, broker, idem, logger):
        self.repo=repo; self.broker=broker; self.idem=idem; self.logger=logger

    def place_entry(self, signal, qty=1, price=None):
        d=dt.date.today().isoformat()
        key=self.idem.make_key(d, signal.symbol, signal.side.value, signal.reason)
        if self.repo.order_exists_by_key(key):
            self.logger.info("duplicate_order_blocked", extra={"extra":{"idempotency_key":key}})
            return None
        state=OrderState.NEW.value
        oid=self.repo.insert_order(signal.signal_id, signal.symbol, signal.side.value, qty, price, key, state)
        state=next_order_state(OrderState(state),"send").value
        self.repo.update_order_state(oid, state)
        req=type("Req",(),{"symbol":signal.symbol,"side":signal.side,"qty":qty,"price":price,"idempotency_key":key})
        result=self.broker.send_order(req)
        self.repo.update_order_state(oid, next_order_state(OrderState.SENT, "ack" if result.success else "reject").value)
        return oid
