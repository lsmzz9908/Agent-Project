def score_level(price, touches=2):
    return min(1.0, 0.3 + touches * 0.25)
