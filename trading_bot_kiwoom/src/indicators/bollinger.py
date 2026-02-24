from __future__ import annotations

def _mean(vals):
    return sum(vals)/len(vals)

def bollinger(close: list[float], period:int=20, std:float=2.0):
    lower=[]; mid=[]; upper=[]
    for i in range(len(close)):
        w=close[max(0,i-period+1):i+1]
        m=_mean(w)
        var=sum((x-m)**2 for x in w)/len(w)
        s=var**0.5
        mid.append(m); lower.append(m-std*s); upper.append(m+std*s)
    return lower, mid, upper
