from __future__ import annotations

import sys
from datetime import datetime
from pathlib import Path

from ..notify.telegram_notifier import TelegramNotifier
from ..service.trading_service import TradingService, load_config

try:
    from PyQt5.QtCore import QThread, pyqtSignal
    from PyQt5.QtWidgets import (
        QApplication,
        QFileDialog,
        QGridLayout,
        QGroupBox,
        QHBoxLayout,
        QLabel,
        QLineEdit,
        QListWidget,
        QMainWindow,
        QMessageBox,
        QPushButton,
        QRadioButton,
        QTextEdit,
        QVBoxLayout,
        QWidget,
    )
except Exception as exc:  # pragma: no cover
    raise RuntimeError("PyQt5 is required for UI mode on Windows.") from exc


class ActionWorker(QThread):
    done = pyqtSignal(dict)
    failed = pyqtSignal(str)

    def __init__(self, service: TradingService, action: str, universe: list[str], interval_sec: int):
        super().__init__()
        self.service = service
        self.action = action
        self.universe = universe
        self.interval_sec = interval_sec

    def run(self):
        try:
            if self.action == "login":
                self.service.login()
                self.done.emit({"status": "login_ok"})
            elif self.action == "start_swing":
                summary = self.service.start_swing_batch(self.universe, live=True)
                self.done.emit(summary.__dict__)
            elif self.action == "start_realtime":
                self.service.start_realtime(self.universe, interval_seconds=self.interval_sec, live=True)
                self.done.emit({"status": "realtime_started"})
            elif self.action == "notify":
                self.service.smoke_notify()
                self.done.emit({"status": "notify_sent"})
            elif self.action == "stop":
                self.service.stop()
                self.done.emit({"status": "stopped"})
        except Exception as exc:
            self.failed.emit(f"{type(exc).__name__}: {exc}")


class MainWindow(QMainWindow):
    status_signal = pyqtSignal(str)

    def __init__(self, cfg_path: str):
        super().__init__()
        self.setWindowTitle("Kiwoom Swing Bot UI")
        self.resize(1000, 700)

        self.cfg = load_config(cfg_path)
        tcfg = self.cfg.get("telegram", {})
        self.notifier = TelegramNotifier(
            enabled=tcfg.get("enabled", False),
            throttle_seconds=tcfg.get("throttle_seconds", 2),
        )
        self.status_signal.connect(self.on_status)
        self.service = TradingService(self.cfg, notifier=self.notifier, status_cb=self._emit_status)
        self.worker: ActionWorker | None = None

        self.universe = self.service.get_default_universe()

        self.lbl_login = QLabel("로그인: 대기")
        self.lbl_account = QLabel("계좌: -")
        self.lbl_mode = QLabel("모드: IDLE")
        self.lbl_uni = QLabel(f"유니버스 종목 수: {len(self.universe)}")
        self.lbl_last_eval = QLabel("최근 평가: -")
        self.lbl_last_order = QLabel("최근 주문: -")
        self.lbl_last_fill = QLabel("최근 체결: -")
        self.lbl_today = QLabel("금일 신호/주문/체결: 0/0/0")

        self.log = QTextEdit()
        self.log.setReadOnly(True)

        self.list_universe = QListWidget()
        self.list_universe.addItems(self.universe)

        self.input_symbol = QLineEdit()
        self.input_symbol.setPlaceholderText("종목코드 6자리")
        self.input_interval = QLineEdit(str(self.cfg.get("realtime", {}).get("interval_seconds", 300)))

        self.radio_swing = QRadioButton("스윙 배치형")
        self.radio_realtime = QRadioButton("상시 실행형")
        self.radio_swing.setChecked(True)

        btn_login = QPushButton("로그인")
        btn_start = QPushButton("선택 모드 시작")
        btn_stop = QPushButton("종료")
        btn_notify = QPushButton("알림 테스트")
        btn_log = QPushButton("로그 보기")

        btn_load_k200 = QPushButton("KOSPI200 로드")
        btn_load_custom = QPushButton("커스텀 로드")
        btn_save_custom = QPushButton("커스텀 저장")
        btn_add = QPushButton("추가")
        btn_del = QPushButton("삭제")

        btn_login.clicked.connect(lambda: self.start_action("login"))
        btn_start.clicked.connect(self.start_selected_mode)
        btn_stop.clicked.connect(lambda: self.start_action("stop"))
        btn_notify.clicked.connect(lambda: self.start_action("notify"))
        btn_log.clicked.connect(self.open_log_file)

        btn_load_k200.clicked.connect(self.load_k200)
        btn_load_custom.clicked.connect(self.load_custom)
        btn_save_custom.clicked.connect(self.save_custom)
        btn_add.clicked.connect(self.add_symbol)
        btn_del.clicked.connect(self.remove_symbol)

        top = QGridLayout()
        top.addWidget(self.lbl_login, 0, 0)
        top.addWidget(self.lbl_account, 0, 1)
        top.addWidget(self.lbl_mode, 0, 2)
        top.addWidget(self.lbl_uni, 1, 0)
        top.addWidget(self.lbl_last_eval, 1, 1)
        top.addWidget(self.lbl_last_order, 1, 2)
        top.addWidget(self.lbl_last_fill, 2, 1)
        top.addWidget(self.lbl_today, 2, 0)

        universe_box = QGroupBox("유니버스 관리")
        ub = QVBoxLayout()
        ub.addWidget(self.list_universe)

        row1 = QHBoxLayout()
        row1.addWidget(btn_load_k200)
        row1.addWidget(btn_load_custom)
        row1.addWidget(btn_save_custom)
        ub.addLayout(row1)

        row2 = QHBoxLayout()
        row2.addWidget(self.input_symbol)
        row2.addWidget(btn_add)
        row2.addWidget(btn_del)
        ub.addLayout(row2)
        universe_box.setLayout(ub)

        control_box = QGroupBox("실행 제어")
        cb = QVBoxLayout()
        cb.addWidget(btn_login)
        cb.addWidget(self.radio_swing)
        cb.addWidget(self.radio_realtime)
        cb.addWidget(QLabel("상시 실행 주기(초)"))
        cb.addWidget(self.input_interval)
        cb.addWidget(btn_start)
        cb.addWidget(btn_stop)
        cb.addWidget(btn_notify)
        cb.addWidget(btn_log)
        control_box.setLayout(cb)

        body = QHBoxLayout()
        body.addWidget(universe_box, 2)
        body.addWidget(control_box, 1)

        root = QVBoxLayout()
        root.addLayout(top)
        root.addLayout(body)
        root.addWidget(QLabel("상태 로그"))
        root.addWidget(self.log)

        central = QWidget()
        central.setLayout(root)
        self.setCentralWidget(central)

    def _emit_status(self, msg: str):
        self.status_signal.emit(msg)

    def _collect_universe(self) -> list[str]:
        return sorted(
            {
                self.list_universe.item(i).text().strip()
                for i in range(self.list_universe.count())
                if len(self.list_universe.item(i).text().strip()) == 6 and self.list_universe.item(i).text().strip().isdigit()
            }
        )

    def _render_stats(self):
        s = self.service.summary
        self.lbl_last_eval.setText(f"최근 평가: {s.last_eval_time or '-'}")
        self.lbl_last_order.setText(f"최근 주문: {s.last_order_time or '-'}")
        self.lbl_last_fill.setText(f"최근 체결: {s.last_fill_time or '-'}")
        self.lbl_today.setText(f"금일 신호/주문/체결: {s.signals_found}/{s.orders_sent}/{s.fills}")

    def _start_worker(self, action: str):
        if self.worker and self.worker.isRunning():
            QMessageBox.information(self, "실행 중", "이미 작업이 실행 중입니다.")
            return
        interval = int(self.input_interval.text() or "300")
        self.worker = ActionWorker(self.service, action, self._collect_universe(), interval)
        self.worker.done.connect(self.on_done)
        self.worker.failed.connect(self.on_failed)
        self.worker.start()

    def start_action(self, action: str):
        self._start_worker(action)

    def start_selected_mode(self):
        if not self.service.is_logged_in():
            QMessageBox.warning(self, "로그인 필요", "먼저 로그인 버튼을 눌러주세요.")
            return
        action = "start_swing" if self.radio_swing.isChecked() else "start_realtime"
        self._start_worker(action)

    def on_done(self, payload: dict):
        self.log_line(f"DONE {payload}")
        if self.service.broker and self.service.broker.account_no:
            self.lbl_account.setText(f"계좌: {self.service._mask_account(self.service.broker.account_no)}")
        self.lbl_mode.setText(f"모드: {self.service.current_mode}")
        self.lbl_uni.setText(f"유니버스 종목 수: {len(self._collect_universe())}")
        self._render_stats()

    def on_failed(self, text: str):
        self.log_line(f"ERROR {text}")
        self.lbl_login.setText("로그인: 실패")
        QMessageBox.warning(self, "오류", text)

    def on_status(self, msg: str):
        self.log_line(msg)
        if "login_start" in msg:
            self.lbl_login.setText("로그인: 시작")
        if "login_success" in msg:
            self.lbl_login.setText("로그인: 성공")
        self._render_stats()

    def log_line(self, text: str):
        self.log.append(f"[{datetime.now().strftime('%H:%M:%S')}] {text}")

    def open_log_file(self):
        p = Path(self.cfg["logging"]["log_path"])
        if not p.exists():
            self.log_line(f"로그 파일 없음: {p}")
            return
        try:
            import os

            os.startfile(str(p.resolve()))  # type: ignore[attr-defined]
        except Exception:
            self.log_line(f"로그 경로: {p.resolve()}")

    def load_k200(self):
        items = self.service.load_universe_csv("data/universe/kospi200.csv") or self.service.load_universe_csv("data/universe_kospi200.csv")
        self.list_universe.clear()
        self.list_universe.addItems(items)
        self.lbl_uni.setText(f"유니버스 종목 수: {len(items)}")
        self.log_line("KOSPI200 로드 완료")

    def load_custom(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "커스텀 유니버스", "data/universe", "Text Files (*.txt *.csv)")
        if not file_path:
            return
        items = self.service.load_universe_csv(file_path) if file_path.endswith(".csv") else self.service.load_custom_universe(file_path)
        self.list_universe.clear()
        self.list_universe.addItems(items)
        self.lbl_uni.setText(f"유니버스 종목 수: {len(items)}")
        self.log_line(f"커스텀 로드: {file_path}")

    def save_custom(self):
        self.service.save_custom_universe(self._collect_universe())
        self.log_line("커스텀 저장: data/universe/custom.txt")

    def add_symbol(self):
        code = "".join(ch for ch in self.input_symbol.text().strip() if ch.isdigit())
        if len(code) != 6:
            QMessageBox.warning(self, "오류", "종목코드 6자리를 입력하세요.")
            return
        if code not in self._collect_universe():
            self.list_universe.addItem(code)
            self.lbl_uni.setText(f"유니버스 종목 수: {len(self._collect_universe())}")

    def remove_symbol(self):
        for item in self.list_universe.selectedItems():
            self.list_universe.takeItem(self.list_universe.row(item))
        self.lbl_uni.setText(f"유니버스 종목 수: {len(self._collect_universe())}")


def main():
    app = QApplication(sys.argv)
    win = MainWindow("config/config.yml")
    win.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
