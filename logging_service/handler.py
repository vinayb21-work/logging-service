import threading

from .destinations import Destination
from .formatters import Formatter
from .levels import LogLevel
from .record import LogRecord


class Handler:
    """
    Pairs a Formatter with a Destination and enforces a minimum level threshold.

    A per-handler lock guarantees that one record's bytes are written atomically —
    no interleaving between concurrent callers hitting the same destination.
    """

    def __init__(
        self,
        formatter: Formatter,
        destination: Destination,
        min_level: LogLevel = LogLevel.DEBUG,
    ) -> None:
        self._formatter = formatter
        self._destination = destination
        self._min_level = min_level
        self._lock = threading.Lock()

    def emit(self, record: LogRecord) -> None:
        if record.level < self._min_level:
            return
        text = self._formatter.format(record)
        with self._lock:
            self._destination.write(text)
