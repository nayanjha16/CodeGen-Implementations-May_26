"""DesignPatternsSolid | kind=design_pattern | label=chain of responsibility | domain=cart | tier=minimal"""
from __future__ import annotations

from __future__ import annotations
from abc import ABC, abstractmethod

class CartHandler(ABC):
    def __init__(self) -> None:
        self.next: CartHandler | None = None

    def link(self, n: CartHandler) -> CartHandler:
        self.next = n
        return n

    def handle(self, level: int, msg: str) -> str:
        if self.can_handle(level):
            return self.do_handle(msg)
        if self.next is not None:
            return self.next.handle(level, msg)
        return "unhandled-cart"

    @abstractmethod
    def can_handle(self, level: int) -> bool: ...
    @abstractmethod
    def do_handle(self, msg: str) -> str: ...

class CartLowHandler(CartHandler):
    def can_handle(self, level: int) -> bool:
        return level <= 1
    def do_handle(self, msg: str) -> str:
        return f"low-cart:{msg}"

class CartHighHandler(CartHandler):
    def can_handle(self, level: int) -> bool:
        return level > 1
    def do_handle(self, msg: str) -> str:
        return f"high-cart:{msg}"
