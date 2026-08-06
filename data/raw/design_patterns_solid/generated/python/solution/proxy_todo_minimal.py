"""DesignPatternsSolid | kind=design_pattern | label=proxy | domain=todo | tier=minimal"""
from __future__ import annotations

from abc import ABC, abstractmethod

class TodoService(ABC):
    @abstractmethod
    def load(self, id: str) -> str: ...

class TodoRealService(TodoService):
    def load(self, id: str) -> str:
        return f"real-todo:{id}"

class TodoProxy(TodoService):
    def __init__(self, allowed: bool) -> None:
        self.allowed = allowed
        self._real: TodoRealService | None = None

    def load(self, id: str) -> str:
        if not self.allowed:
            return "denied"
        if self._real is None:
            self._real = TodoRealService()
        return self._real.load(id)
