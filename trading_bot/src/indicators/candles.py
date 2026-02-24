from __future__ import annotations

def body_ratio(o: float, h: float, l: float, c: float) -> float:
    rng = max(h-l, 1e-9)
    return abs(c-o)/rng

def is_bullish_reversal(o: float, h: float, l: float, c: float, min_body_ratio: float) -> bool:
    return c > o and body_ratio(o,h,l,c) >= min_body_ratio

def is_bearish_reversal(o: float, h: float, l: float, c: float, min_body_ratio: float) -> bool:
    return c < o and body_ratio(o,h,l,c) >= min_body_ratio

def bullish_engulf(prev_o, prev_c, o, c) -> bool:
    return prev_c < prev_o and c > o and c >= prev_o and o <= prev_c

def bearish_engulf(prev_o, prev_c, o, c) -> bool:
    return prev_c > prev_o and c < o and o >= prev_c and c <= prev_o
