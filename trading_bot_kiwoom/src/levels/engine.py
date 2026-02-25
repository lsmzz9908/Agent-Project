from .pivots import find_pivots
from .clustering import cluster_levels
from .scoring import score_level

class LevelEngine:
    def build(self, close):
        piv=find_pivots(close)
        lv=cluster_levels(piv)
        return [{"price":x, "score":score_level(x)} for x in lv]
