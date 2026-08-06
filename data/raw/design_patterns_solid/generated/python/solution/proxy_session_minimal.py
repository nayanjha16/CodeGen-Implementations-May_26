"""DesignPatternsSolid | kind=design_pattern | label=proxy | domain=session | tier=minimal"""
from __future__ import annotations

from abc import ABC, abstractmethod

class SessionService(ABC):
    @abstractmethod
    def load(self, id: str) -> str: ...

class SessionRealService(SessionService):
    def load(self, id: str) -> str:
        return f"real-session:{id}"

class SessionProxy(SessionService):
    def __init__(self, allowed: bool) -> None:
        self.allowed = allowed
        self._real: SessionRealService | None = None

    def load(self, id: str) -> str:
        if not self.allowed:
            return "denied"
        if self._real is None:
            self._real = SessionRealService()
        return self._real.load(id)
