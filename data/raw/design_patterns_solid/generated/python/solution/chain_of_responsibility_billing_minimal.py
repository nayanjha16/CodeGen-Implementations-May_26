"""DesignPatternsSolid | kind=design_pattern | label=chain of responsibility | domain=billing | tier=minimal"""
from __future__ import annotations

from __future__ import annotations
from abc import ABC, abstractmethod

class BillingHandler(ABC):
    def __init__(self) -> None:
        self.next: BillingHandler | None = None

    def link(self, n: BillingHandler) -> BillingHandler:
        self.next = n
        return n

    def handle(self, level: int, msg: str) -> str:
        if self.can_handle(level):
            return self.do_handle(msg)
        if self.next is not None:
            return self.next.handle(level, msg)
        return "unhandled-billing"

    @abstractmethod
    def can_handle(self, level: int) -> bool: ...
    @abstractmethod
    def do_handle(self, msg: str) -> str: ...

class BillingLowHandler(BillingHandler):
    def can_handle(self, level: int) -> bool:
        return level <= 1
    def do_handle(self, msg: str) -> str:
        return f"low-billing:{msg}"

class BillingHighHandler(BillingHandler):
    def can_handle(self, level: int) -> bool:
        return level > 1
    def do_handle(self, msg: str) -> str:
        return f"high-billing:{msg}"
