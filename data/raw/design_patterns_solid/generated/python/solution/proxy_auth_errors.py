"""DesignPatternsSolid | kind=design_pattern | label=proxy | domain=auth | tier=errors"""
from __future__ import annotations

from abc import ABC, abstractmethod

class AuthService(ABC):
    @abstractmethod
    def load(self, id: str) -> str: ...

class AuthRealService(AuthService):
    def load(self, id: str) -> str:
        return f"real-auth:{id}"

class AuthProxy(AuthService):
    def __init__(self, allowed: bool) -> None:
        self.allowed = allowed
        self._real: AuthRealService | None = None

    def load(self, id: str) -> str:
        if not self.allowed:
            return "denied"
        if self._real is None:
            self._real = AuthRealService()
        return self._real.load(id)
