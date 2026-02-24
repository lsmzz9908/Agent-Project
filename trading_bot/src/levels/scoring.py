from __future__ import annotations

def score_level(touches: int, reaction: float, recency: float, w: dict) -> float:
    return touches*w["w_touches"] + reaction*w["w_reaction"] + recency*w["w_recency"]
