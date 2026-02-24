from __future__ import annotations

def atr(rows: list[dict], period=14):
    trs=[]; out=[]
    prev_close=None
    for r in rows:
        h,l,c=r['high'],r['low'],r['close']
        tr=max(h-l, abs(h-(prev_close if prev_close is not None else c)), abs(l-(prev_close if prev_close is not None else c)))
        trs.append(tr)
        w=trs[max(0,len(trs)-period):]
        out.append(sum(w)/len(w))
        prev_close=c
    return out
