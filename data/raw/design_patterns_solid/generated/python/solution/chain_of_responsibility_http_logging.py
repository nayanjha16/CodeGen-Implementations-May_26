"""DesignPatternsSolid | kind=design_pattern | label=chain of responsibility | domain=http | tier=logging"""
from __future__ import annotations

from __future__ import annotations
from abc import ABC, abstractmethod

class HttpHandler(ABC):
    def __init__(self) -> None:
        self.next: HttpHandler | None = None

    def link(self, n: HttpHandler) -> HttpHandler:
        self.next = n
        return n

    def handle(self, level: int, msg: str) -> str:
        if self.can_handle(level):
            return self.do_handle(msg)
        if self.next is not None:
            return self.next.handle(level, msg)
        return "unhandled-http"

    @abstractmethod
    def can_handle(self, level: int) -> bool: ...
    @abstractmethod
    def do_handle(self, msg: str) -> str: ...

class HttpLowHandler(HttpHandler):
    def can_handle(self, level: int) -> bool:
        return level <= 1
    def do_handle(self, msg: str) -> str:
        return f"low-http:{msg}"

class HttpHighHandler(HttpHandler):
    def can_handle(self, level: int) -> bool:
        return level > 1
    def do_handle(self, msg: str) -> str:
        return f"high-http:{msg}"
