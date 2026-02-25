def cluster_levels(pivots, width=0.02):
    levels=[]
    for _,p in pivots:
        if not levels or abs(levels[-1]-p)/p>width:
            levels.append(p)
    return sorted(levels)
