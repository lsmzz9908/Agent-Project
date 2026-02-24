def bullish_divergence(price_lows, osc_lows):
    if len(price_lows)<2 or len(osc_lows)<2: return False
    return price_lows[-1] < price_lows[-2] and osc_lows[-1] > osc_lows[-2]
