def position_size(cash, entry, stop, risk_per_trade=0.005):
    risk_amt=cash*risk_per_trade
    unit=max(entry-stop,1)
    return int(risk_amt/unit)
