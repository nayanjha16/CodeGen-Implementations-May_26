"""DesignPatternsSolid | kind=design_pattern | label=chain of responsibility | domain=ticket | tier=logging"""
from __future__ import annotations

from __future__ import annotations
from abc import ABC, abstractmethod

class TicketHandler(ABC):
    def __init__(self) -> None:
        self.next: TicketHandler | None = None

    def link(self, n: TicketHandler) -> TicketHandler:
        self.next = n
        return n

    def handle(self, level: int, msg: str) -> str:
        if self.can_handle(level):
            return self.do_handle(msg)
        if self.next is not None:
            return self.next.handle(level, msg)
        return "unhandled-ticket"

    @abstractmethod
    def can_handle(self, level: int) -> bool: ...
    @abstractmethod
    def do_handle(self, msg: str) -> str: ...

class TicketLowHandler(TicketHandler):
    def can_handle(self, level: int) -> bool:
        return level <= 1
    def do_handle(self, msg: str) -> str:
        return f"low-ticket:{msg}"

class TicketHighHandler(TicketHandler):
    def can_handle(self, level: int) -> bool:
        return level > 1
    def do_handle(self, msg: str) -> str:
        return f"high-ticket:{msg}"
