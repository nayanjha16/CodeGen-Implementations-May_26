"""DesignPatternsSolid | kind=design_pattern | label=proxy | domain=editor | tier=minimal"""
from __future__ import annotations

from abc import ABC, abstractmethod

class EditorService(ABC):
    @abstractmethod
    def load(self, id: str) -> str: ...

class EditorRealService(EditorService):
    def load(self, id: str) -> str:
        return f"real-editor:{id}"

class EditorProxy(EditorService):
    def __init__(self, allowed: bool) -> None:
        self.allowed = allowed
        self._real: EditorRealService | None = None

    def load(self, id: str) -> str:
        if not self.allowed:
            return "denied"
        if self._real is None:
            self._real = EditorRealService()
        return self._real.load(id)
