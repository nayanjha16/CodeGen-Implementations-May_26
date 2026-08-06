"""DesignPatternsSolid | kind=design_pattern | label=chain of responsibility | domain=database | tier=errors"""
from __future__ import annotations

from __future__ import annotations
from abc import ABC, abstractmethod

class DatabaseHandler(ABC):
    def __init__(self) -> None:
        self.next: DatabaseHandler | None = None

    def link(self, n: DatabaseHandler) -> DatabaseHandler:
        self.next = n
        return n

    def handle(self, level: int, msg: str) -> str:
        if self.can_handle(level):
            return self.do_handle(msg)
        if self.next is not None:
            return self.next.handle(level, msg)
        return "unhandled-database"

    @abstractmethod
    def can_handle(self, level: int) -> bool: ...
    @abstractmethod
    def do_handle(self, msg: str) -> str: ...

class DatabaseLowHandler(DatabaseHandler):
    def can_handle(self, level: int) -> bool:
        return level <= 1
    def do_handle(self, msg: str) -> str:
        return f"low-database:{msg}"

class DatabaseHighHandler(DatabaseHandler):
    def can_handle(self, level: int) -> bool:
        return level > 1
    def do_handle(self, msg: str) -> str:
        return f"high-database:{msg}"
