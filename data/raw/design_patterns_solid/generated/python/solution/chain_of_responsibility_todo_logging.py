"""DesignPatternsSolid | kind=design_pattern | label=chain of responsibility | domain=todo | tier=logging"""
from __future__ import annotations

from __future__ import annotations
from abc import ABC, abstractmethod

class TodoHandler(ABC):
    def __init__(self) -> None:
        self.next: TodoHandler | None = None

    def link(self, n: TodoHandler) -> TodoHandler:
        self.next = n
        return n

    def handle(self, level: int, msg: str) -> str:
        if self.can_handle(level):
            return self.do_handle(msg)
        if self.next is not None:
            return self.next.handle(level, msg)
        return "unhandled-todo"

    @abstractmethod
    def can_handle(self, level: int) -> bool: ...
    @abstractmethod
    def do_handle(self, msg: str) -> str: ...

class TodoLowHandler(TodoHandler):
    def can_handle(self, level: int) -> bool:
        return level <= 1
    def do_handle(self, msg: str) -> str:
        return f"low-todo:{msg}"

class TodoHighHandler(TodoHandler):
    def can_handle(self, level: int) -> bool:
        return level > 1
    def do_handle(self, msg: str) -> str:
        return f"high-todo:{msg}"
