"""DesignPatternsSolid | kind=design_pattern | label=chain of responsibility | domain=logging | tier=minimal"""
from __future__ import annotations

from __future__ import annotations
from abc import ABC, abstractmethod

class LoggingHandler(ABC):
    def __init__(self) -> None:
        self.next: LoggingHandler | None = None

    def link(self, n: LoggingHandler) -> LoggingHandler:
        self.next = n
        return n

    def handle(self, level: int, msg: str) -> str:
        if self.can_handle(level):
            return self.do_handle(msg)
        if self.next is not None:
            return self.next.handle(level, msg)
        return "unhandled-logging"

    @abstractmethod
    def can_handle(self, level: int) -> bool: ...
    @abstractmethod
    def do_handle(self, msg: str) -> str: ...

class LoggingLowHandler(LoggingHandler):
    def can_handle(self, level: int) -> bool:
        return level <= 1
    def do_handle(self, msg: str) -> str:
        return f"low-logging:{msg}"

class LoggingHighHandler(LoggingHandler):
    def can_handle(self, level: int) -> bool:
        return level > 1
    def do_handle(self, msg: str) -> str:
        return f"high-logging:{msg}"
