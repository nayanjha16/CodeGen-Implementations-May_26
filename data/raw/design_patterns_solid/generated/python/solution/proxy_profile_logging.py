"""DesignPatternsSolid | kind=design_pattern | label=proxy | domain=profile | tier=logging"""
from __future__ import annotations

from abc import ABC, abstractmethod

class ProfileService(ABC):
    @abstractmethod
    def load(self, id: str) -> str: ...

class ProfileRealService(ProfileService):
    def load(self, id: str) -> str:
        return f"real-profile:{id}"

class ProfileProxy(ProfileService):
    def __init__(self, allowed: bool) -> None:
        self.allowed = allowed
        self._real: ProfileRealService | None = None

    def load(self, id: str) -> str:
        if not self.allowed:
            return "denied"
        if self._real is None:
            self._real = ProfileRealService()
        return self._real.load(id)
