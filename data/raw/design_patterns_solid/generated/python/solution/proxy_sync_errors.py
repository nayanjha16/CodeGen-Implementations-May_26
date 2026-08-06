"""DesignPatternsSolid | kind=design_pattern | label=proxy | domain=sync | tier=errors"""
from __future__ import annotations

from abc import ABC, abstractmethod

class SyncService(ABC):
    @abstractmethod
    def load(self, id: str) -> str: ...

class SyncRealService(SyncService):
    def load(self, id: str) -> str:
        return f"real-sync:{id}"

class SyncProxy(SyncService):
    def __init__(self, allowed: bool) -> None:
        self.allowed = allowed
        self._real: SyncRealService | None = None

    def load(self, id: str) -> str:
        if not self.allowed:
            return "denied"
        if self._real is None:
            self._real = SyncRealService()
        return self._real.load(id)
