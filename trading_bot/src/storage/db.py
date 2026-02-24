from __future__ import annotations

import sqlite3
from pathlib import Path

from src.storage.models import SCHEMA


class Database:
    def __init__(self, path: str):
        db_path = Path(path)
        db_path.parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(str(db_path))

    def init(self):
        cur = self.conn.cursor()
        for ddl in SCHEMA.values():
            cur.execute(ddl)
        self.conn.commit()
