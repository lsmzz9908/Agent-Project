from __future__ import annotations
import threading, queue
try:
    from PyQt5.QtWidgets import QApplication
    from PyQt5.QAxContainer import QAxWidget
    PYQT_AVAILABLE = True
except Exception:
    QApplication = object
    QAxWidget = object
    PYQT_AVAILABLE = False

class KiwoomAPI:
    """Event-driven wrapper; in non-Windows env it runs in stub mode for paper/backtest."""
    def __init__(self, logger):
        self.logger=logger
        self.connected=False
        self.event_queue: queue.Queue = queue.Queue()
        self.account_list=[]
        self._thread=None
        self._callbacks={"tr":[],"chejan":[]}

    def connect(self):
        if not PYQT_AVAILABLE:
            self.connected=True
            self.account_list=["1234567890"]
            self.logger.info("stub_login_success")
            return 0
        app = QApplication.instance() or QApplication([])
        self.ocx = QAxWidget("KHOPENAPI.KHOpenAPICtrl.1")
        self.ocx.OnEventConnect.connect(self._on_event_connect)
        self.ocx.OnReceiveTrData.connect(self._on_receive_tr_data)
        self.ocx.OnReceiveChejanData.connect(self._on_receive_chejan)
        self.ocx.dynamicCall("CommConnect()")
        if self._thread is None:
            self._thread=threading.Thread(target=app.exec_, daemon=True)
            self._thread.start()
        return 0

    def _on_event_connect(self, err_code):
        self.connected=(err_code==0)
        self.logger.info("login_event", extra={"extra":{"err_code":err_code}})

    def _on_receive_tr_data(self, *args):
        self.event_queue.put(("tr", args))

    def _on_receive_chejan(self, *args):
        self.event_queue.put(("chejan", args))

    def register_callback(self, kind, cb):
        self._callbacks[kind].append(cb)

    def pump_events(self):
        while not self.event_queue.empty():
            kind,payload=self.event_queue.get()
            for cb in self._callbacks.get(kind,[]):
                cb(payload)

    def get_login_info(self, tag="ACCNO"):
        return ";".join(self.account_list)

    def send_order(self, *args, **kwargs):
        self.logger.info("send_order_called", extra={"extra":{"args":str(args)}})
        return 0
