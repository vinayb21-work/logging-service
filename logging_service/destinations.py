from abc import ABC, abstractmethod
from typing import IO


class Destination(ABC):
    @abstractmethod
    def write(self, text: str) -> None: ...


class ConsoleDestination(Destination):
    def write(self, text: str) -> None:
        print(text)


class FileDestination(Destination):
    def __init__(self, path: str) -> None:
        self._file: IO[str] = open(path, "a", encoding="utf-8")

    def write(self, text: str) -> None:
        self._file.write(text + "\n")
        self._file.flush()

    def close(self) -> None:
        self._file.close()
