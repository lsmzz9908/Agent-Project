SCHEMA = {
"signals": """
CREATE TABLE IF NOT EXISTS signals (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  ts TEXT, market TEXT, ticker TEXT, side TEXT, trigger TEXT,
  reason TEXT, indicators_json TEXT, levels_json TEXT, trade_plan_json TEXT
)""",
"orders": """
CREATE TABLE IF NOT EXISTS orders (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  ts TEXT, market TEXT, ticker TEXT, side TEXT, qty REAL,
  order_type TEXT, status TEXT, broker_order_id TEXT, raw_json TEXT
)""",
"fills": """
CREATE TABLE IF NOT EXISTS fills (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  ts TEXT, broker_order_id TEXT, qty REAL, price REAL, fee REAL, raw_json TEXT
)""",
"positions": """
CREATE TABLE IF NOT EXISTS positions (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  ts TEXT, market TEXT, ticker TEXT, side TEXT, qty REAL,
  entry_price REAL, stop_loss REAL, take_profit_1 REAL,
  trailing_stop REAL, time_stop_days INTEGER, status TEXT
)""",
"errors": """
CREATE TABLE IF NOT EXISTS errors (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  ts TEXT, component TEXT, code TEXT, message TEXT, raw_json TEXT
)"""
}
