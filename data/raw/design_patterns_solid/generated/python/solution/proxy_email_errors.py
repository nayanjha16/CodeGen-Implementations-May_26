"""DesignPatternsSolid | kind=design_pattern | label=proxy | domain=email | tier=errors"""
from __future__ import annotations

from abc import ABC, abstractmethod

class EmailService(ABC):
    @abstractmethod
    def load(self, id: str) -> str: ...

class EmailRealService(EmailService):
    def load(self, id: str) -> str:
        return f"real-email:{id}"

class EmailProxy(EmailService):
    def __init__(self, allowed: bool) -> None:
        self.allowed = allowed
        self._real: EmailRealService | None = None

    def load(self, id: str) -> str:
        if not self.allowed:
            return "denied"
        if self._real is None:
            self._real = EmailRealService()
        return self._real.load(id)
