"""
Gmail Monitor — periodically polls the Gmail inbox for new messages
and runs each through the analysis pipeline callback.
"""

import threading
import time
from typing import Callable

from ingestion.email_fetcher import GmailFetcher


class GmailMonitor:
    """
    Wraps ``GmailFetcher`` in a background thread that polls at a
    configurable interval and invokes a callback for each **new** email.
    """

    def __init__(
        self,
        fetcher: GmailFetcher,
        interval_seconds: int = 60,
        max_emails: int = 10,
    ):
        self.fetcher = fetcher
        self.interval = interval_seconds
        self.max_emails = max_emails
        self._seen: set[str] = set()
        self._running = False
        self._thread: threading.Thread | None = None

    # ------------------------------------------------------------------ #
    #  Public API
    # ------------------------------------------------------------------ #

    def start_monitoring(self, callback: Callable):
        """
        Start polling in a daemon thread.

        ``callback`` receives ``(msg_id: str, email_msg)`` arguments.
        """
        if self._running:
            return

        self._running = True
        self._thread = threading.Thread(
            target=self._poll_loop,
            args=(callback,),
            daemon=True,
        )
        self._thread.start()

    def stop_monitoring(self):
        """Signal the polling loop to stop."""
        self._running = False

    @property
    def is_running(self) -> bool:
        return self._running

    # ------------------------------------------------------------------ #
    #  Private
    # ------------------------------------------------------------------ #

    def _poll_loop(self, callback: Callable):
        while self._running:
            try:
                messages = self.fetcher.fetch_recent(
                    max_results=self.max_emails
                )
                for msg_id, msg in messages:
                    if msg_id not in self._seen:
                        self._seen.add(msg_id)
                        callback(msg_id, msg)
            except Exception as e:
                print("Gmail Monitor Error:", e)
            time.sleep(self.interval)
