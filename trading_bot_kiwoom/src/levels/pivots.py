def find_pivots(values, left_right=3):
    piv=[]
    for i in range(left_right, len(values)-left_right):
        w=values[i-left_right:i+left_right+1]
        if values[i]==max(w) or values[i]==min(w):
            piv.append((i, float(values[i])))
    return piv
