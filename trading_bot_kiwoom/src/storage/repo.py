from __future__ import annotations
from .db import connect
from .models import SCHEMA

class Repository:
    def __init__(self, db_path):
        self.conn=connect(db_path)
        for ddl in SCHEMA: self.conn.execute(ddl)
        self.conn.commit()

    def insert_signal(self, signal):
        self.conn.execute("INSERT OR REPLACE INTO signals(signal_id,symbol,side,score,reason) VALUES(?,?,?,?,?)",(signal.signal_id, signal.symbol, signal.side.value, signal.score, signal.reason))
        self.conn.commit()

    def order_exists_by_key(self, key):
        cur=self.conn.execute("SELECT 1 FROM orders WHERE idempotency_key=?",(key,))
        return cur.fetchone() is not None

    def insert_order(self, signal_id, symbol, side, qty, price, key, state):
        cur=self.conn.execute("INSERT INTO orders(signal_id,symbol,side,qty,price,idempotency_key,state) VALUES(?,?,?,?,?,?,?)",(signal_id,symbol,side,qty,price,key,state))
        self.conn.commit(); return cur.lastrowid

    def update_order_state(self, oid, state):
        self.conn.execute("UPDATE orders SET state=? WHERE id=?",(state, oid)); self.conn.commit()
