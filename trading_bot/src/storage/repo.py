from __future__ import annotations
import json
from dataclasses import asdict

class Repo:
    def __init__(self, db):
        self.db = db

    def save_signal(self, signal):
        cur = self.db.conn.cursor()
        cur.execute("INSERT INTO signals(ts,market,ticker,side,trigger,reason,indicators_json,levels_json,trade_plan_json) VALUES(?,?,?,?,?,?,?,?,?)", (
            str(signal.ts), signal.symbol.market, signal.symbol.ticker, signal.side, signal.trigger, signal.reason,
            json.dumps(signal.indicators, default=str), json.dumps([asdict(l) for l in signal.levels], default=str), json.dumps(asdict(signal.trade_plan), default=str)
        ))
        self.db.conn.commit()
