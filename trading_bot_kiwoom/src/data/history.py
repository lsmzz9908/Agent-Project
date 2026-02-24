from __future__ import annotations
import random, datetime as dt

def load_sample_ohlcv(symbol: str, bars: int=120):
    random.seed(42)
    rows=[]
    price=50000.0
    for i in range(bars):
        date=(dt.date.today()-dt.timedelta(days=bars-i)).isoformat()
        drift=120
        noise=random.randint(-500,500)
        open_=price
        close=max(1000, price+drift+noise)
        high=max(open_,close)+random.randint(50,300)
        low=min(open_,close)-random.randint(50,300)
        volume=random.randint(200000,1200000)
        rows.append({"date":date,"open":open_,"high":high,"low":low,"close":close,"volume":volume})
        price=close
    return rows
