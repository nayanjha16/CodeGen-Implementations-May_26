"""DesignPatternsSolid | kind=design_pattern | label=chain of responsibility | domain=cache | tier=minimal"""
from __future__ import annotations

from __future__ import annotations
from abc import ABC, abstractmethod

class CacheHandler(ABC):
    def __init__(self) -> None:
        self.next: CacheHandler | None = None

    def link(self, n: CacheHandler) -> CacheHandler:
        self.next = n
        return n

    def handle(self, level: int, msg: str) -> str:
        if self.can_handle(level):
            return self.do_handle(msg)
        if self.next is not None:
            return self.next.handle(level, msg)
        return "unhandled-cache"

    @abstractmethod
    def can_handle(self, level: int) -> bool: ...
    @abstractmethod
    def do_handle(self, msg: str) -> str: ...

class CacheLowHandler(CacheHandler):
    def can_handle(self, level: int) -> bool:
        return level <= 1
    def do_handle(self, msg: str) -> str:
        return f"low-cache:{msg}"

class CacheHighHandler(CacheHandler):
    def can_handle(self, level: int) -> bool:
        return level > 1
    def do_handle(self, msg: str) -> str:
        return f"high-cache:{msg}"
