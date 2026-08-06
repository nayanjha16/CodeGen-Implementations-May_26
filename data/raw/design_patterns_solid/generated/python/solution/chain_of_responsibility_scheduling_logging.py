"""DesignPatternsSolid | kind=design_pattern | label=chain of responsibility | domain=scheduling | tier=logging"""
from __future__ import annotations

from __future__ import annotations
from abc import ABC, abstractmethod

class SchedulingHandler(ABC):
    def __init__(self) -> None:
        self.next: SchedulingHandler | None = None

    def link(self, n: SchedulingHandler) -> SchedulingHandler:
        self.next = n
        return n

    def handle(self, level: int, msg: str) -> str:
        if self.can_handle(level):
            return self.do_handle(msg)
        if self.next is not None:
            return self.next.handle(level, msg)
        return "unhandled-scheduling"

    @abstractmethod
    def can_handle(self, level: int) -> bool: ...
    @abstractmethod
    def do_handle(self, msg: str) -> str: ...

class SchedulingLowHandler(SchedulingHandler):
    def can_handle(self, level: int) -> bool:
        return level <= 1
    def do_handle(self, msg: str) -> str:
        return f"low-scheduling:{msg}"

class SchedulingHighHandler(SchedulingHandler):
    def can_handle(self, level: int) -> bool:
        return level > 1
    def do_handle(self, msg: str) -> str:
        return f"high-scheduling:{msg}"
