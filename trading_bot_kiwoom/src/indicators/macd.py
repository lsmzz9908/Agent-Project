from __future__ import annotations

def _ema(vals, span):
    alpha=2/(span+1)
    out=[]
    for v in vals:
        out.append(v if not out else alpha*v+(1-alpha)*out[-1])
    return out

def macd(close: list[float], fast=12, slow=26, signal=9):
    f=_ema(close,fast); s=_ema(close,slow)
    line=[a-b for a,b in zip(f,s)]
    sig=_ema(line,signal)
    hist=[a-b for a,b in zip(line,sig)]
    return line,sig,hist
