from __future__ import annotations
import sqlite3
from src.storage.models import SCHEMA

class Database:
    def __init__(self, path: str):
        self.conn = sqlite3.connect(path)

    def init(self):
        cur = self.conn.cursor()
        for ddl in SCHEMA.values():
            cur.execute(ddl)
        self.conn.commit()
