from __future__ import annotations

import time
from datetime import datetime
from pathlib import Path
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

    def _read_credentials(self) -> tuple[str, str]:
        env_path = Path(__file__).resolve().parents[2] / "telegram.env.txt"
        if not env_path.exists():
            return "", ""

        parsed: dict[str, str] = {}
        for raw in env_path.read_text(encoding="utf-8").splitlines():
            line = raw.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            parsed[key.strip()] = value.strip().strip('"').strip("'")

        token = parsed.get("TELEGRAM_BOT_TOKEN", "")
        chat_id = parsed.get("TELEGRAM_CHAT_ID", "")
        return token, chat_id

    def send(self, text: str) -> None:
        if not self.enabled:
            return

        token, chat_id = self._read_credentials()
        if not token or not chat_id:
            self._log_warning("telegram_missing_env_file_or_keys")
            return

        body_text = f"{self._now_prefix()} {text}"
        if not self._can_send(body_text):
            return

        url = f"https://api.telegram.org/bot{token}/sendMessage"
        payload = {"chat_id": chat_id, "text": body_text}

        try:
            import requests

            resp = requests.post(url, json=payload, timeout=5)
            if self.logger:
                self.logger.info(
                    "telegram_send",
                    extra={"extra": {"status": resp.status_code, "body": resp.text[:200]}},
                )
            if resp.status_code >= 400:
                self._log_warning(f"telegram_send_failed status={resp.status_code}")
        except Exception as exc:
            self._log_warning(f"telegram_send_exception type={type(exc).__name__}")
