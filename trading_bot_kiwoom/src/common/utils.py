from __future__ import annotations
import hashlib
import uuid

def make_signal_id() -> str:
    return str(uuid.uuid4())

def stable_hash(payload: str) -> str:
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()[:16]
