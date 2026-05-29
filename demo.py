"""
Demonstrates the logging service with:
  - two simultaneous destinations (console + file)
  - two independent formatters (plain text vs JSON)
  - per-destination minimum-level filtering
  - concurrent writes from multiple threads (lock safety)
"""

import threading

from logging_service import (
    ConsoleDestination,
    FileDestination,
    Handler,
    JSONFormatter,
    LogLevel,
    Logger,
    PlainTextFormatter,
)

LOG_FILE = "/tmp/demo_app.log"


def build_logger() -> Logger:
    # Console: plain text, show everything DEBUG and above
    console_handler = Handler(
        formatter=PlainTextFormatter(),
        destination=ConsoleDestination(),
        min_level=LogLevel.DEBUG,
    )

    # File: JSON, only WARN and above
    file_handler = Handler(
        formatter=JSONFormatter(),
        destination=FileDestination(LOG_FILE),
        min_level=LogLevel.WARN,
    )

    return Logger(handlers=[console_handler, file_handler])


def worker(logger: Logger, worker_id: int) -> None:
    logger.debug(f"worker {worker_id} starting")
    logger.info(f"worker {worker_id} processing")
    logger.warn(f"worker {worker_id} slow response detected")
    logger.error(f"worker {worker_id} encountered an error")


def main() -> None:
    logger = build_logger()

    # Single-threaded warmup
    logger.info("application starting")

    # Concurrent writes from 5 threads — records must not interleave
    threads = [
        threading.Thread(target=worker, args=(logger, i), name=f"worker-{i}")
        for i in range(5)
    ]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    logger.fatal("application shutting down")
    print(f"\n[JSON records written to {LOG_FILE}]")


if __name__ == "__main__":
    main()
