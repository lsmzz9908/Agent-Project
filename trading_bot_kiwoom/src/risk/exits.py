def stop_loss(level, atr, buffer_k=0.4):
    return level - atr*buffer_k

def trailing_stop(highest, atr, atr_k=2.5):
    return highest - atr*atr_k
