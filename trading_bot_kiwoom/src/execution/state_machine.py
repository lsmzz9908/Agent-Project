from __future__ import annotations
from enum import Enum

class OrderState(str, Enum):
    NEW="NEW"; SENT="SENT"; ACK="ACK"; PARTIAL="PARTIAL"; FILLED="FILLED"; REJECTED="REJECTED"; CANCELED="CANCELED"; EXPIRED="EXPIRED"

class PositionState(str, Enum):
    NONE="NONE"; OPENING="OPENING"; OPEN="OPEN"; CLOSING="CLOSING"; CLOSED="CLOSED"

ORDER_TRANSITIONS={
    OrderState.NEW:{"send":OrderState.SENT},
    OrderState.SENT:{"ack":OrderState.ACK, "reject":OrderState.REJECTED},
    OrderState.ACK:{"partial":OrderState.PARTIAL, "fill":OrderState.FILLED, "cancel":OrderState.CANCELED},
    OrderState.PARTIAL:{"partial":OrderState.PARTIAL, "fill":OrderState.FILLED, "cancel":OrderState.CANCELED},
}

def next_order_state(state:OrderState,event:str)->OrderState:
    if state in ORDER_TRANSITIONS and event in ORDER_TRANSITIONS[state]:
        return ORDER_TRANSITIONS[state][event]
    return state

def next_position_state(state:PositionState,event:str)->PositionState:
    table={
        (PositionState.NONE,"order_sent"):PositionState.OPENING,
        (PositionState.OPENING,"filled"):PositionState.OPEN,
        (PositionState.OPEN,"close_sent"):PositionState.CLOSING,
        (PositionState.CLOSING,"filled"):PositionState.CLOSED,
    }
    return table.get((state,event), state)
