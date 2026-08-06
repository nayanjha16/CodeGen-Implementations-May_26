"""DesignPatternsSolid | kind=design_pattern | label=chain of responsibility | domain=search | tier=errors"""
from __future__ import annotations

from __future__ import annotations
from abc import ABC, abstractmethod

class SearchHandler(ABC):
    def __init__(self) -> None:
        self.next: SearchHandler | None = None

    def link(self, n: SearchHandler) -> SearchHandler:
        self.next = n
        return n

    def handle(self, level: int, msg: str) -> str:
        if self.can_handle(level):
            return self.do_handle(msg)
        if self.next is not None:
            return self.next.handle(level, msg)
        return "unhandled-search"

    @abstractmethod
    def can_handle(self, level: int) -> bool: ...
    @abstractmethod
    def do_handle(self, msg: str) -> str: ...

class SearchLowHandler(SearchHandler):
    def can_handle(self, level: int) -> bool:
        return level <= 1
    def do_handle(self, msg: str) -> str:
        return f"low-search:{msg}"

class SearchHighHandler(SearchHandler):
    def can_handle(self, level: int) -> bool:
        return level > 1
    def do_handle(self, msg: str) -> str:
        return f"high-search:{msg}"
