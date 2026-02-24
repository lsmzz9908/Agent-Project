from ..indicators.candles import body_ratio

def trigger_reversal_bb(row, lower_band, min_body_ratio=0.45):
    return row['low'] <= lower_band and body_ratio(row['open'],row['high'],row['low'],row['close']) >= min_body_ratio

def trigger_div_macd(divergence_ok, macd_hist_prev, macd_hist_now):
    return divergence_ok and macd_hist_prev <= 0 < macd_hist_now
