from src.execution.state_machine import OrderState, next_order_state

def test_order_state_flow():
    s=OrderState.NEW
    s=next_order_state(s,'send')
    s=next_order_state(s,'ack')
    s=next_order_state(s,'partial')
    s=next_order_state(s,'fill')
    assert s==OrderState.FILLED
