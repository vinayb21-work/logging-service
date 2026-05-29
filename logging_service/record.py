from dataclasses import dataclass
from datetime import datetime

from .levels import LogLevel


@dataclass(frozen=True)
class LogRecord:
    """Immutable snapshot of a single log event."""
    timestamp: datetime
    level: LogLevel
    message: str
    thread_name: str
