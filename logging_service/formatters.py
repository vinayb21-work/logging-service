import json
from abc import ABC, abstractmethod

from .record import LogRecord


class Formatter(ABC):
    @abstractmethod
    def format(self, record: LogRecord) -> str: ...


class PlainTextFormatter(Formatter):
    def format(self, record: LogRecord) -> str:
        ts = record.timestamp.strftime("%Y-%m-%dT%H:%M:%S.%f")
        return f"[{ts}] [{record.level}] [{record.thread_name}] {record.message}"


class JSONFormatter(Formatter):
    def format(self, record: LogRecord) -> str:
        return json.dumps({
            "timestamp": record.timestamp.isoformat(),
            "level": str(record.level),
            "thread": record.thread_name,
            "message": record.message,
        })
