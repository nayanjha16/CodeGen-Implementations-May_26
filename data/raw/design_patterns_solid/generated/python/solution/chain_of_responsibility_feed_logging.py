"""DesignPatternsSolid | kind=design_pattern | label=chain of responsibility | domain=feed | tier=logging"""
from __future__ import annotations

from __future__ import annotations
from abc import ABC, abstractmethod

class FeedHandler(ABC):
    def __init__(self) -> None:
        self.next: FeedHandler | None = None

    def link(self, n: FeedHandler) -> FeedHandler:
        self.next = n
        return n

    def handle(self, level: int, msg: str) -> str:
        if self.can_handle(level):
            return self.do_handle(msg)
        if self.next is not None:
            return self.next.handle(level, msg)
        return "unhandled-feed"

    @abstractmethod
    def can_handle(self, level: int) -> bool: ...
    @abstractmethod
    def do_handle(self, msg: str) -> str: ...

class FeedLowHandler(FeedHandler):
    def can_handle(self, level: int) -> bool:
        return level <= 1
    def do_handle(self, msg: str) -> str:
        return f"low-feed:{msg}"

class FeedHighHandler(FeedHandler):
    def can_handle(self, level: int) -> bool:
        return level > 1
    def do_handle(self, msg: str) -> str:
        return f"high-feed:{msg}"
