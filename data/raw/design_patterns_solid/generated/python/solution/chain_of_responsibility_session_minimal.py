"""DesignPatternsSolid | kind=design_pattern | label=chain of responsibility | domain=session | tier=minimal"""
from __future__ import annotations

from __future__ import annotations
from abc import ABC, abstractmethod

class SessionHandler(ABC):
    def __init__(self) -> None:
        self.next: SessionHandler | None = None

    def link(self, n: SessionHandler) -> SessionHandler:
        self.next = n
        return n

    def handle(self, level: int, msg: str) -> str:
        if self.can_handle(level):
            return self.do_handle(msg)
        if self.next is not None:
            return self.next.handle(level, msg)
        return "unhandled-session"

    @abstractmethod
    def can_handle(self, level: int) -> bool: ...
    @abstractmethod
    def do_handle(self, msg: str) -> str: ...

class SessionLowHandler(SessionHandler):
    def can_handle(self, level: int) -> bool:
        return level <= 1
    def do_handle(self, msg: str) -> str:
        return f"low-session:{msg}"

class SessionHighHandler(SessionHandler):
    def can_handle(self, level: int) -> bool:
        return level > 1
    def do_handle(self, msg: str) -> str:
        return f"high-session:{msg}"
