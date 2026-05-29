# logging-service

A lightweight, thread-safe logging library for Python.

---

## Entities

### `LogLevel`
Enum defining severity levels.

| Value | Int |
|-------|-----|
| `DEBUG` | 0 |
| `INFO` | 1 |
| `WARN` | 2 |
| `ERROR` | 3 |
| `FATAL` | 4 |

---

### `LogRecord`
Immutable snapshot of a single log event. Created internally by `Logger`.

| Field | Type |
|-------|------|
| `timestamp` | `datetime` |
| `level` | `LogLevel` |
| `message` | `str` |
| `thread_name` | `str` |

---

### `Logger`
Entry point. Fan-out dispatcher — sends each log call to every registered `Handler`.

| Method | Description |
|--------|-------------|
| `__init__(handlers?)` | Optional initial list of handlers |
| `add_handler(handler)` | Register a handler |
| `debug(message)` | Log at DEBUG level |
| `info(message)` | Log at INFO level |
| `warn(message)` | Log at WARN level |
| `error(message)` | Log at ERROR level |
| `fatal(message)` | Log at FATAL level |

---

### `Handler`
Pairs a `Formatter` with a `Destination`. Filters by minimum level and guarantees atomic writes.

| Method | Description |
|--------|-------------|
| `__init__(formatter, destination, min_level?)` | `min_level` defaults to `DEBUG` |
| `emit(record)` | Format and write record if it meets the level threshold |

---

### `Formatter` (abstract)
Defines how a `LogRecord` is serialized to a string.

| Subclass | Output |
|----------|--------|
| `PlainTextFormatter` | `[timestamp] [level] [thread_name] message` |
| `JSONFormatter` | `{"timestamp": ..., "level": ..., "thread": ..., "message": ...}` |

---

### `Destination` (abstract)
Defines where formatted output is written.

| Subclass | Method | Description |
|----------|--------|-------------|
| `ConsoleDestination` | `write(text)` | Prints to stdout |
| `FileDestination` | `__init__(path)` | Opens file in append mode |
| | `write(text)` | Writes line and flushes |
| | `close()` | Closes the file |

---

## Quick Start

```python
from logging_service import Logger, Handler, PlainTextFormatter, ConsoleDestination, LogLevel

logger = Logger()
handler = Handler(
    formatter=PlainTextFormatter(),
    destination=ConsoleDestination(),
    min_level=LogLevel.INFO,
)
logger.add_handler(handler)

logger.info("Service started")
logger.error("Something went wrong")
```
