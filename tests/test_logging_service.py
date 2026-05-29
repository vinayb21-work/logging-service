"""
Unit tests for the logging service.
All tests use an in-memory destination so no filesystem I/O is needed.
"""

import threading
from datetime import datetime, timezone

import pytest

from logging_service import (
    Handler,
    JSONFormatter,
    LogLevel,
    LogRecord,
    Logger,
    PlainTextFormatter,
)
from logging_service.destinations import Destination


# ------------------------------------------------------------------ #
# Test double                                                          #
# ------------------------------------------------------------------ #

class CapturingDestination(Destination):
    """Records every write call for assertion."""

    def __init__(self) -> None:
        self.lines: list[str] = []
        self._lock = threading.Lock()

    def write(self, text: str) -> None:
        with self._lock:
            self.lines.append(text)


# ------------------------------------------------------------------ #
# Helpers                                                              #
# ------------------------------------------------------------------ #

def _record(level: LogLevel, message: str = "hello") -> LogRecord:
    return LogRecord(
        timestamp=datetime.now(timezone.utc),
        level=level,
        message=message,
        thread_name="main",
    )


# ------------------------------------------------------------------ #
# LogLevel ordering                                                    #
# ------------------------------------------------------------------ #

def test_level_ordering():
    assert LogLevel.DEBUG < LogLevel.INFO < LogLevel.WARN < LogLevel.ERROR < LogLevel.FATAL


# ------------------------------------------------------------------ #
# PlainTextFormatter                                                   #
# ------------------------------------------------------------------ #

def test_plain_text_formatter_contains_all_fields():
    record = _record(LogLevel.INFO, "test message")
    text = PlainTextFormatter().format(record)
    assert "INFO" in text
    assert "test message" in text
    assert "main" in text


# ------------------------------------------------------------------ #
# JSONFormatter                                                        #
# ------------------------------------------------------------------ #

def test_json_formatter_is_valid_json():
    import json
    record = _record(LogLevel.ERROR, "boom")
    text = JSONFormatter().format(record)
    data = json.loads(text)
    assert data["level"] == "ERROR"
    assert data["message"] == "boom"
    assert data["thread"] == "main"
    assert "timestamp" in data


# ------------------------------------------------------------------ #
# Handler — level filtering                                            #
# ------------------------------------------------------------------ #

def test_handler_drops_records_below_min_level():
    dest = CapturingDestination()
    handler = Handler(PlainTextFormatter(), dest, min_level=LogLevel.WARN)

    handler.emit(_record(LogLevel.DEBUG))
    handler.emit(_record(LogLevel.INFO))
    handler.emit(_record(LogLevel.WARN))
    handler.emit(_record(LogLevel.ERROR))

    assert len(dest.lines) == 2
    assert all("WARN" in line or "ERROR" in line for line in dest.lines)


def test_handler_passes_records_at_min_level():
    dest = CapturingDestination()
    handler = Handler(PlainTextFormatter(), dest, min_level=LogLevel.INFO)
    handler.emit(_record(LogLevel.INFO, "exactly at threshold"))
    assert len(dest.lines) == 1


# ------------------------------------------------------------------ #
# Logger — fan-out                                                     #
# ------------------------------------------------------------------ #

def test_logger_fans_out_to_all_handlers():
    dest1 = CapturingDestination()
    dest2 = CapturingDestination()
    logger = Logger(handlers=[
        Handler(PlainTextFormatter(), dest1),
        Handler(PlainTextFormatter(), dest2),
    ])
    logger.info("broadcast")
    assert len(dest1.lines) == 1
    assert len(dest2.lines) == 1


def test_logger_respects_per_handler_min_level():
    verbose_dest = CapturingDestination()
    quiet_dest = CapturingDestination()
    logger = Logger(handlers=[
        Handler(PlainTextFormatter(), verbose_dest, min_level=LogLevel.DEBUG),
        Handler(PlainTextFormatter(), quiet_dest, min_level=LogLevel.ERROR),
    ])
    logger.debug("low")
    logger.info("medium")
    logger.error("high")

    assert len(verbose_dest.lines) == 3
    assert len(quiet_dest.lines) == 1


def test_logger_severity_convenience_methods():
    dest = CapturingDestination()
    logger = Logger(handlers=[Handler(PlainTextFormatter(), dest)])
    logger.debug("d")
    logger.info("i")
    logger.warn("w")
    logger.error("e")
    logger.fatal("f")
    assert len(dest.lines) == 5
    levels_written = [line.split("]")[1].strip()[1:] for line in dest.lines]
    assert levels_written == ["DEBUG", "INFO", "WARN", "ERROR", "FATAL"]


# ------------------------------------------------------------------ #
# Thread safety — no interleaving                                      #
# ------------------------------------------------------------------ #

def test_concurrent_writes_are_atomic():
    """
    Each write is a fixed-width string. With proper locking no two records
    should share the same output slot, so the total count must match exactly.
    """
    dest = CapturingDestination()
    logger = Logger(handlers=[Handler(PlainTextFormatter(), dest)])

    n_threads = 20
    writes_per_thread = 50

    def worker():
        for _ in range(writes_per_thread):
            logger.info("concurrent message")

    threads = [threading.Thread(target=worker) for _ in range(n_threads)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    assert len(dest.lines) == n_threads * writes_per_thread
