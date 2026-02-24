def total_return(equity_curve):
    return (equity_curve[-1]/equity_curve[0])-1 if len(equity_curve)>1 else 0.0
