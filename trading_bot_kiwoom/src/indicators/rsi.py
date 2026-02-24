from __future__ import annotations

def rsi(close: list[float], period:int=14)->list[float]:
    if len(close) < 2:
        return [50.0]*len(close)
    gains=[]; losses=[]
    out=[50.0]
    for i in range(1,len(close)):
        d=close[i]-close[i-1]
        gains.append(max(d,0.0)); losses.append(max(-d,0.0))
        start=max(0,len(gains)-period)
        avg_gain=sum(gains[start:])/max(1,len(gains[start:]))
        avg_loss=sum(losses[start:])/max(1,len(losses[start:]))
        rs=avg_gain/(avg_loss if avg_loss else 1e-9)
        out.append(100-(100/(1+rs)))
    return out
