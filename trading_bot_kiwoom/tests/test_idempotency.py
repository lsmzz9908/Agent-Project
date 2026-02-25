from src.execution.idempotency import IdempotencyService

def test_same_payload_same_key():
    idem=IdempotencyService('{date}:{symbol}:{side}:{signal_hash}')
    k1=idem.make_key('2026-01-01','005930','BUY','abc')
    k2=idem.make_key('2026-01-01','005930','BUY','abc')
    assert k1==k2
