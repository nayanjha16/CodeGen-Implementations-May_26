"""DesignPatternsSolid | kind=design_pattern | label=proxy | domain=notes | tier=errors"""
from __future__ import annotations

from abc import ABC, abstractmethod

class NotesService(ABC):
    @abstractmethod
    def load(self, id: str) -> str: ...

class NotesRealService(NotesService):
    def load(self, id: str) -> str:
        return f"real-notes:{id}"

class NotesProxy(NotesService):
    def __init__(self, allowed: bool) -> None:
        self.allowed = allowed
        self._real: NotesRealService | None = None

    def load(self, id: str) -> str:
        if not self.allowed:
            return "denied"
        if self._real is None:
            self._real = NotesRealService()
        return self._real.load(id)
