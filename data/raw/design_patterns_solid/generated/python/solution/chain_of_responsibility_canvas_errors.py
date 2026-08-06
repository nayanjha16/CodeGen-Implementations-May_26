"""DesignPatternsSolid | kind=design_pattern | label=chain of responsibility | domain=canvas | tier=errors"""
from __future__ import annotations

from __future__ import annotations
from abc import ABC, abstractmethod

class CanvasHandler(ABC):
    def __init__(self) -> None:
        self.next: CanvasHandler | None = None

    def link(self, n: CanvasHandler) -> CanvasHandler:
        self.next = n
        return n

    def handle(self, level: int, msg: str) -> str:
        if self.can_handle(level):
            return self.do_handle(msg)
        if self.next is not None:
            return self.next.handle(level, msg)
        return "unhandled-canvas"

    @abstractmethod
    def can_handle(self, level: int) -> bool: ...
    @abstractmethod
    def do_handle(self, msg: str) -> str: ...

class CanvasLowHandler(CanvasHandler):
    def can_handle(self, level: int) -> bool:
        return level <= 1
    def do_handle(self, msg: str) -> str:
        return f"low-canvas:{msg}"

class CanvasHighHandler(CanvasHandler):
    def can_handle(self, level: int) -> bool:
        return level > 1
    def do_handle(self, msg: str) -> str:
        return f"high-canvas:{msg}"
