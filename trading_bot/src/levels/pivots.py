from __future__ import annotations
import pandas as pd

def pivot_highs(df: pd.DataFrame, lr: int) -> list[int]:
    idx = []
    for i in range(lr, len(df)-lr):
        win = df["high"].iloc[i-lr:i+lr+1]
        if df["high"].iloc[i] == win.max():
            idx.append(i)
    return idx

def pivot_lows(df: pd.DataFrame, lr: int) -> list[int]:
    idx = []
    for i in range(lr, len(df)-lr):
        win = df["low"].iloc[i-lr:i+lr+1]
        if df["low"].iloc[i] == win.min():
            idx.append(i)
    return idx
