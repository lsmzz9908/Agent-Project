from __future__ import annotations
import os
import time
from datetime import datetime, timedelta
import requests
import pandas as pd

class ShinhanBroker:
    def __init__(self, base_url: str = "https://api.shinhansec.example", session: requests.Session | None = None):
        self.base_url = base_url
        self.session = session or requests.Session()
        self.app_key = os.getenv("SHINHAN_APP_KEY", "")
        self.app_secret = os.getenv("SHINHAN_APP_SECRET", "")
        self.account_no = os.getenv("SHINHAN_ACCOUNT_NO", "")
        self.account_pw = os.getenv("SHINHAN_ACCOUNT_PW", "")
        self.token = None
        self.token_expiry = datetime.min

    def _auth_headers(self):
        if datetime.utcnow() >= self.token_expiry:
            self._refresh_token()
        return {"Authorization": f"Bearer {self.token}", "X-APP-KEY": self.app_key}

    def _refresh_token(self):
        resp = self.session.post(f"{self.base_url}/oauth/token", json={"appKey": self.app_key, "appSecret": self.app_secret}, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        self.token = data["access_token"]
        expires_in = int(data.get("expires_in", 600))
        self.token_expiry = datetime.utcnow() + timedelta(seconds=max(60, expires_in - 30))

    def _request(self, method: str, path: str, retries: int = 3, **kwargs):
        for i in range(retries):
            try:
                headers = kwargs.pop("headers", {})
                headers.update(self._auth_headers())
                r = self.session.request(method, f"{self.base_url}{path}", headers=headers, timeout=10, **kwargs)
                if r.status_code == 401:
                    self._refresh_token()
                    continue
                if r.status_code in (429, 500, 502, 503):
                    time.sleep(2 ** i)
                    continue
                r.raise_for_status()
                return r.json()
            except requests.RequestException:
                if i == retries - 1:
                    raise
                time.sleep(2 ** i)
        raise RuntimeError("request_failed")

    def get_daily_ohlcv(self, symbol, lookback: int = 500):
        data = self._request("GET", f"/market/{symbol.market}/daily", params={"ticker": symbol.ticker, "n": lookback})
        return pd.DataFrame(data["candles"])

    def place_order(self, symbol, side: str, qty: float, order_type: str, price: float | None = None, market: str | None = None):
        payload = {"accountNo": self.account_no, "ticker": symbol.ticker, "side": side, "qty": qty, "orderType": order_type, "price": price}
        return self._request("POST", f"/orders/{market or symbol.market}", json=payload)

    def cancel_order(self, order_id: str):
        return self._request("POST", "/orders/cancel", json={"orderId": order_id})

    def modify_order(self, order_id: str, new_price: float | None = None, new_qty: float | None = None):
        return self._request("POST", "/orders/modify", json={"orderId": order_id, "price": new_price, "qty": new_qty})

    def get_positions(self):
        return self._request("GET", "/account/positions", params={"accountNo": self.account_no})

    def get_balance(self):
        return self._request("GET", "/account/balance", params={"accountNo": self.account_no})

    def get_fills(self):
        return self._request("GET", "/account/fills", params={"accountNo": self.account_no})
