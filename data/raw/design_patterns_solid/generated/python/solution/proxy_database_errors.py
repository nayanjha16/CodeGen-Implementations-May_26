"""DesignPatternsSolid | kind=design_pattern | label=proxy | domain=database | tier=errors"""
from __future__ import annotations

from abc import ABC, abstractmethod

class DatabaseService(ABC):
    @abstractmethod
    def load(self, id: str) -> str: ...

class DatabaseRealService(DatabaseService):
    def load(self, id: str) -> str:
        return f"real-database:{id}"

class DatabaseProxy(DatabaseService):
    def __init__(self, allowed: bool) -> None:
        self.allowed = allowed
        self._real: DatabaseRealService | None = None

    def load(self, id: str) -> str:
        if not self.allowed:
            return "denied"
        if self._real is None:
            self._real = DatabaseRealService()
        return self._real.load(id)
