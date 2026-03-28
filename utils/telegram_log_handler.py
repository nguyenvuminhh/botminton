"""
Custom logging handler that forwards log records to a Telegram group chat.
Uses urllib (stdlib) so no extra dependencies are needed.
Only records at WARNING level and above are forwarded to avoid spam.
"""

import logging
import urllib.parse
import urllib.request


class TelegramLogHandler(logging.Handler):
    """Sends log records to a Telegram chat via the Bot API (synchronous HTTP)."""

    def __init__(self, bot_token: str, chat_id: str, level: int = logging.WARNING):
        super().__init__(level)
        self._url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        self._chat_id = chat_id

    def emit(self, record: logging.LogRecord) -> None:
        try:
            text = self.format(record)
            # Telegram max message length is 4096 chars
            text = text[:4096]
            data = urllib.parse.urlencode({"chat_id": self._chat_id, "text": text}).encode()
            req = urllib.request.Request(self._url, data=data, method="POST")
            with urllib.request.urlopen(req, timeout=5):
                pass
        except Exception:
            self.handleError(record)
