def body_ratio(open_, high, low, close):
    rng=max(high-low,1e-9)
    return abs(close-open_)/rng
