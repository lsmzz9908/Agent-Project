from __future__ import annotations

import json
import os
import time
from datetime import datetime
from zoneinfo import ZoneInfo


class TelegramNotifier:
    def __init__(
        self,
        enabled: bool,
        token_env: str = "TELEGRAM_BOT_TOKEN",
        chat_id_env: str = "TELEGRAM_CHAT_ID",
        throttle_seconds: int = 2,
        logger=None,
    ):
        self.enabled = bool(enabled)
        self.token_env = token_env
        self.chat_id_env = chat_id_env
        self.throttle_seconds = int(throttle_seconds)
        self.logger = logger
        self._last_sent_by_text: dict[str, float] = {}

    def _log_warning(self, message: str):
        if self.logger:
            self.logger.warning(message)

    def _now_prefix(self) -> str:
        ts = datetime.now(ZoneInfo("Asia/Seoul")).strftime("%Y-%m-%d %H:%M:%S")
        return f"[{ts}]"

    def _can_send(self, text: str) -> bool:
        now = time.time()
        prev = self._last_sent_by_text.get(text)
        if prev is not None and (now - prev) < self.throttle_seconds:
            return False
        self._last_sent_by_text[text] = now
        return True

    def send(self, text: str) -> None:
        if not self.enabled:
            return

        token = os.getenv(self.token_env)
        chat_id = os.getenv(self.chat_id_env)
        if not token or not chat_id:
            self._log_warning("telegram_missing_env")
            return

        body_text = f"{self._now_prefix()} {text}"
        if not self._can_send(body_text):
            return

        url = f"https://api.telegram.org/bot{token}/sendMessage"
        payload = {"chat_id": chat_id, "text": body_text}

        try:
            try:
                import requests  # type: ignore

                resp = requests.post(url, json=payload, timeout=5)
                if resp.status_code >= 400:
                    self._log_warning(f"telegram_send_failed status={resp.status_code}")
                return
            except Exception:
                pass

            from urllib import request

            req = request.Request(
                url,
                data=json.dumps(payload).encode("utf-8"),
                headers={"Content-Type": "application/json"},
                method="POST",
            )
            with request.urlopen(req, timeout=5) as resp:  # nosec B310
                if int(getattr(resp, "status", 200)) >= 400:
                    self._log_warning("telegram_send_failed status>=400")
        except Exception as exc:
            self._log_warning(f"telegram_send_exception type={type(exc).__name__}")
