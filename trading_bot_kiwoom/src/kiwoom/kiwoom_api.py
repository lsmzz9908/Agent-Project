from __future__ import annotations

import platform
import queue
import threading
from typing import Any, Callable

from .rate_limiter import TrRateLimiter

try:
    from PyQt5.QtCore import QEventLoop, QTimer
    from PyQt5.QAxContainer import QAxWidget
    from PyQt5.QtWidgets import QApplication

    PYQT_AVAILABLE = True
except Exception:
    QEventLoop = None
    QTimer = None
    QApplication = None
    QAxWidget = None
    PYQT_AVAILABLE = False


class KiwoomAPI:
    """Real Kiwoom OpenAPI+ wrapper (QAxWidget based)."""

    def __init__(self, logger):
        self.logger = logger
        self.connected = False
        self.account_list: list[str] = []

        self._app = None
        self.ocx = None
        self._login_loop = None
        self._last_login_err: int | None = None

        self._callbacks: dict[str, list[Callable[[Any], None]]] = {
            "tr": [],
            "chejan": [],
            "real": [],
        }

        self._tr_worker_queue: queue.Queue = queue.Queue()
        self._tr_request_meta: dict[str, dict[str, Any]] = {}
        self._rq_seq = 0

        self._tr_rate_limiter = TrRateLimiter(delay_sec=0.25)
        self._tr_worker_stop = threading.Event()
        self._tr_worker = threading.Thread(target=self._tr_worker_loop, daemon=True)
        self._tr_worker.start()

    @staticmethod
    def _activex_error() -> RuntimeError:
        return RuntimeError("KHOpenAPI ActiveX not instantiated. Check KOA Studio/HTS install and 32/64-bit.")

    def _ensure_openapi(self):
        current_os = platform.system()
        if current_os != "Windows":
            raise RuntimeError(f"live mode supports only Windows. detected_os={current_os}")
        if not PYQT_AVAILABLE:
            raise RuntimeError("PyQt5/QAxContainer import failed on Windows. Check PyQt5 and ActiveX environment.")

        self._app = QApplication.instance() or QApplication([])
        if self.ocx is None:
            ok = False
            try:
                self.ocx = QAxWidget()
                ok = self.ocx.setControl("KHOPENAPI.KHOpenAPICtrl.1")
            except Exception as exc:
                self.ocx = None
                self.logger.error("setControl_ok=False")
                raise self._activex_error() from exc

            self.logger.info(f"setControl_ok={ok}")
            if not ok:
                self.ocx = None
                raise self._activex_error()

            self.ocx.OnEventConnect.connect(self._on_event_connect)
            self.ocx.OnReceiveTrData.connect(self._on_receive_tr_data)
            self.ocx.OnReceiveChejanData.connect(self._on_receive_chejan_data)
            if hasattr(self.ocx, "OnReceiveRealData"):
                self.ocx.OnReceiveRealData.connect(self._on_receive_real_data)

    def connect_and_login(self, timeout_sec: int = 120):
        self._ensure_openapi()
        self._login_loop = QEventLoop()
        self._last_login_err = None

        timer = QTimer()
        timer.setSingleShot(True)

        def _on_timeout():
            if self._login_loop and self._login_loop.isRunning():
                self._login_loop.quit()

        timer.timeout.connect(_on_timeout)
        timer.start(timeout_sec * 1000)

        self.logger.info("kiwoom_login_start")
        self.ocx.dynamicCall("CommConnect()")
        self.logger.info("commconnect_called")
        self._login_loop.exec_()

        if self._last_login_err is None:
            raise RuntimeError("Kiwoom login failed: timeout waiting OnEventConnect")
        if self._last_login_err != 0:
            raise RuntimeError(f"Kiwoom login failed: err_code={self._last_login_err}")

        self.connected = True
        self.logger.info("kiwoom_login_success")

        acc_raw = self.get_login_info("ACCNO")
        self.logger.info(f"accno_loaded={acc_raw}")
        self.account_list = [a.strip() for a in acc_raw.split(";") if a.strip()]
        if not self.account_list:
            self.logger.error("account_list_empty")
            raise RuntimeError("GetLoginInfo('ACCNO') returned empty account list.")
        self.logger.info("account_list_loaded", extra={"extra": {"accounts": self.account_list}})
        return True

    def get_login_info(self, tag: str = "ACCNO") -> str:
        self._ensure_openapi()
        return str(self.ocx.dynamicCall("GetLoginInfo(QString)", tag))

    def set_input_value(self, key: str, value: str):
        self.ocx.dynamicCall("SetInputValue(QString, QString)", key, value)

    def comm_rq_data(self, rqname: str, trcode: str, prev_next: int, screen_no: str):
        return int(self.ocx.dynamicCall("CommRqData(QString, QString, int, QString)", rqname, trcode, prev_next, screen_no))

    def request_tr(self, trcode: str, inputs: dict[str, str], screen_no: str = "1000", prev_next: int = 0, rqname: str | None = None):
        self._rq_seq += 1
        rqname = rqname or f"RQ_{trcode}_{self._rq_seq}"
        self._tr_request_meta[rqname] = {
            "trcode": trcode,
            "screen_no": screen_no,
            "inputs": inputs,
            "prev_next": prev_next,
        }

        def _task():
            for k, v in inputs.items():
                self.set_input_value(k, v)
            rc = self.comm_rq_data(rqname, trcode, prev_next, screen_no)
            if rc != 0:
                raise RuntimeError(f"CommRqData failed: {rqname}/{trcode}/rc={rc}")

        self._tr_rate_limiter.submit(_task, wait=True, timeout_sec=10.0)
        return rqname

    def send_order(
        self,
        rqname: str,
        screen_no: str,
        acc_no: str,
        order_type: int,
        code: str,
        qty: int,
        price: int,
        hoga: str,
        org_order_no: str = "",
    ) -> int:
        return int(
            self.ocx.dynamicCall(
                "SendOrder(QString, QString, QString, int, QString, int, int, QString, QString)",
                rqname,
                screen_no,
                acc_no,
                order_type,
                code,
                qty,
                price,
                hoga,
                org_order_no,
            )
        )

    def register_callback(self, kind: str, cb: Callable[[Any], None]):
        self._callbacks.setdefault(kind, []).append(cb)

    def _on_event_connect(self, err_code: int):
        self.logger.info(f"on_event_connect_received err_code={err_code}")
        self._last_login_err = int(err_code)
        if self._login_loop and self._login_loop.isRunning():
            self._login_loop.quit()

    def _on_receive_tr_data(self, scr_no, rqname, trcode, record_name, prev_next, *_):
        payload = {
            "screen_no": str(scr_no),
            "rqname": str(rqname),
            "trcode": str(trcode),
            "record_name": str(record_name),
            "prev_next": str(prev_next),
            "request_meta": self._tr_request_meta.get(str(rqname), {}),
        }
        self._tr_worker_queue.put(("tr", payload))

    def _on_receive_chejan_data(self, gubun, item_cnt, fid_list):
        payload = {"gubun": str(gubun), "item_cnt": str(item_cnt), "fid_list": str(fid_list)}
        self._tr_worker_queue.put(("chejan", payload))

    def _safe_get_chejan_data(self, fid: int) -> str:
        if self.ocx is None:
            return ""
        try:
            return str(self.ocx.dynamicCall("GetChejanData(int)", fid)).strip()
        except Exception:
            return ""

    def _parse_chejan_payload(self, payload: dict[str, str]) -> dict[str, Any]:
        # FID refs: 9203(order_no), 9001(code), 900(qty), 911(filled_qty), 910(fill_price), 931(avg_price)
        order_no = self._safe_get_chejan_data(9203)
        code = self._safe_get_chejan_data(9001).lstrip("A")
        qty = self._safe_get_chejan_data(900)
        filled_qty = self._safe_get_chejan_data(911)
        fill_price = self._safe_get_chejan_data(910)
        avg_price = self._safe_get_chejan_data(931)

        event_type = "chejan"
        try:
            f_qty = int(filled_qty or "0")
            t_qty = int(qty or "0")
            if f_qty > 0 and f_qty < t_qty:
                event_type = "partial_fill"
            elif f_qty > 0 and (t_qty == 0 or f_qty >= t_qty):
                event_type = "filled"
        except ValueError:
            pass

        parsed = dict(payload)
        parsed.update(
            {
                "event_type": event_type,
                "order_no": order_no,
                "symbol": code,
                "qty": qty,
                "filled_qty": filled_qty,
                "fill_price": fill_price,
                "avg_price": avg_price,
            }
        )
        return parsed

    def _on_receive_real_data(self, code, real_type, real_data):
        payload = {"code": str(code), "real_type": str(real_type), "real_data": str(real_data)}
        self._tr_worker_queue.put(("real", payload))

    def _tr_worker_loop(self):
        while not self._tr_worker_stop.is_set():
            try:
                kind, payload = self._tr_worker_queue.get(timeout=0.2)
            except queue.Empty:
                continue

            if kind == "chejan":
                payload = self._parse_chejan_payload(payload)

            for cb in self._callbacks.get(kind, []):
                cb(payload)

    def close(self):
        self._tr_worker_stop.set()
        self._tr_rate_limiter.stop()
