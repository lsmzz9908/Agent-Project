from __future__ import annotations
import time

class OrderManager:
    def __init__(self, broker, logger):
        self.broker = broker
        self.logger = logger

    def submit_with_retry(self, *args, retries: int = 3, **kwargs):
        for i in range(retries):
            try:
                return self.broker.place_order(*args, **kwargs)
            except Exception as e:
                self.logger.error("order_submit_failed", extra={"attempt": i+1, "error": str(e)})
                time.sleep(2 ** i)
        raise RuntimeError("order_submit_exhausted")

    def sync_fills(self):
        return self.broker.get_fills()
