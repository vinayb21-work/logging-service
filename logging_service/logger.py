import threading
from datetime import datetime, timezone

from .handler import Handler
from .levels import LogLevel
from .record import LogRecord


class Logger:
    """
    Fan-out logger: a single log call is dispatched to every registered Handler.
    Each Handler applies its own level filter, formatter, and destination lock.
    """

    def __init__(self, handlers: list[Handler] | None = None) -> None:
        self._handlers: list[Handler] = list(handlers or [])

    def add_handler(self, handler: Handler) -> None:
        self._handlers.append(handler)

    # ------------------------------------------------------------------ #
    # Public API                                                           #
    # ------------------------------------------------------------------ #

    def debug(self, message: str) -> None:
        self._log(LogLevel.DEBUG, message)

    def info(self, message: str) -> None:
        self._log(LogLevel.INFO, message)

    def warn(self, message: str) -> None:
        self._log(LogLevel.WARN, message)

    def error(self, message: str) -> None:
        self._log(LogLevel.ERROR, message)

    def fatal(self, message: str) -> None:
        self._log(LogLevel.FATAL, message)

    # ------------------------------------------------------------------ #
    # Internal                                                             #
    # ------------------------------------------------------------------ #

    def _log(self, level: LogLevel, message: str) -> None:
        record = LogRecord(
            timestamp=datetime.now(timezone.utc),
            level=level,
            message=message,
            thread_name=threading.current_thread().name,
        )
        for handler in self._handlers:
            handler.emit(record)
