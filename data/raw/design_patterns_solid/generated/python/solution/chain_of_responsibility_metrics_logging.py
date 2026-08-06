"""DesignPatternsSolid | kind=design_pattern | label=chain of responsibility | domain=metrics | tier=logging"""
from __future__ import annotations

from __future__ import annotations
from abc import ABC, abstractmethod

class MetricsHandler(ABC):
    def __init__(self) -> None:
        self.next: MetricsHandler | None = None

    def link(self, n: MetricsHandler) -> MetricsHandler:
        self.next = n
        return n

    def handle(self, level: int, msg: str) -> str:
        if self.can_handle(level):
            return self.do_handle(msg)
        if self.next is not None:
            return self.next.handle(level, msg)
        return "unhandled-metrics"

    @abstractmethod
    def can_handle(self, level: int) -> bool: ...
    @abstractmethod
    def do_handle(self, msg: str) -> str: ...

class MetricsLowHandler(MetricsHandler):
    def can_handle(self, level: int) -> bool:
        return level <= 1
    def do_handle(self, msg: str) -> str:
        return f"low-metrics:{msg}"

class MetricsHighHandler(MetricsHandler):
    def can_handle(self, level: int) -> bool:
        return level > 1
    def do_handle(self, msg: str) -> str:
        return f"high-metrics:{msg}"
