from __future__ import annotations

import datetime as dt

from .state_machine import OrderState, next_order_state


class OrderManager:
    def __init__(self, repo, broker, idem, logger, notifier):
        self.repo = repo
        self.broker = broker
        self.idem = idem
        self.logger = logger
        if notifier is None:
            raise ValueError("OrderManager requires a notifier instance.")
        self.notifier = notifier
        self._notified_order_state: set[tuple[str, str]] = set()

    def _notify(self, text: str):
        self.notifier.send(text)

    def _notify_order_state_once(self, order_no: str, state: str, text: str):
        key = (order_no, state)
        if key in self._notified_order_state:
            return
        self._notified_order_state.add(key)
        self._notify(text)

    def place_entry(self, signal, qty=1, price=None):
        d = dt.date.today().isoformat()
        key = self.idem.make_key(d, signal.symbol, signal.side.value, signal.reason)
        if self.repo.order_exists_by_key(key):
            self.logger.info("duplicate_order_blocked", extra={"extra": {"idempotency_key": key}})
            return None

        state = OrderState.NEW.value
        oid = self.repo.insert_order(signal.signal_id, signal.symbol, signal.side.value, qty, price, key, state)
        state = next_order_state(OrderState(state), "send").value
        self.repo.update_order_state(oid, state)

        self._notify_order_state_once(
            str(oid),
            "submitted",
            f"🟡 주문 접수: {signal.symbol} {signal.side.value} {qty} @ {price if price is not None else 'MKT'}",
        )

        req = type(
            "Req",
            (),
            {"symbol": signal.symbol, "side": signal.side, "qty": qty, "price": price, "idempotency_key": key},
        )
        try:
            result = self.broker.send_order(req)
        except Exception as exc:
            self.repo.update_order_state(oid, next_order_state(OrderState.SENT, "reject").value)
            self._notify_order_state_once(str(oid), "rejected", f"🔴 주문 거부: {type(exc).__name__}")
            raise

        final_state = next_order_state(OrderState.SENT, "ack" if result.success else "reject").value
        self.repo.update_order_state(oid, final_state)
        if result.success:
            self.logger.info("order_ack", extra={"extra": {"order_no": result.order_no}})
        else:
            msg = str(result.message).lower()
            if "cancel" in msg:
                self._notify_order_state_once(str(result.order_no), "canceled", f"⚪ 주문 취소: {result.order_no}")
            else:
                self._notify_order_state_once(str(result.order_no), "rejected", f"🔴 주문 거부: {result.message}")
        return oid

    def handle_chejan(self, payload: dict):
        event = payload.get("event_type", "")
        symbol = payload.get("symbol") or payload.get("code") or "UNKNOWN"
        filled_qty = payload.get("filled_qty") or payload.get("qty") or "?"
        qty = payload.get("qty") or "?"
        fill_price = payload.get("fill_price") or payload.get("avg_price") or "?"

        if event == "partial_fill":
            self._notify(f"🔵 부분체결: {symbol} {filled_qty}/{qty} @ {fill_price}")
        elif event == "filled":
            self._notify(f"🔵 체결완료: {symbol} {qty} @ {fill_price}")
        elif event == "position_opened":
            self._notify(
                f"🟣 포지션 오픈: {symbol} qty={payload.get('qty', '?')} entry={payload.get('entry_price', '?')} SL={payload.get('sl', '?')}"
            )
        elif event == "position_closed":
            self._notify(
                f"🟢 포지션 청산: {symbol} pnl={payload.get('pnl', '?')} ({payload.get('pnl_pct', '?')}%)"
            )
        elif event == "stop_loss_triggered":
            self._notify(f"🔴 손절: {symbol} {payload.get('reason', '')}")
        elif event == "take_profit_triggered":
            self._notify(f"🟢 익절: {symbol} {payload.get('reason', '')}")
