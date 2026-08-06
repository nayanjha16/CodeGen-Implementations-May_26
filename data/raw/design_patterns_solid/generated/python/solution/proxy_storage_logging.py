"""DesignPatternsSolid | kind=design_pattern | label=proxy | domain=storage | tier=logging"""
from __future__ import annotations

from abc import ABC, abstractmethod

class StorageService(ABC):
    @abstractmethod
    def load(self, id: str) -> str: ...

class StorageRealService(StorageService):
    def load(self, id: str) -> str:
        return f"real-storage:{id}"

class StorageProxy(StorageService):
    def __init__(self, allowed: bool) -> None:
        self.allowed = allowed
        self._real: StorageRealService | None = None

    def load(self, id: str) -> str:
        if not self.allowed:
            return "denied"
        if self._real is None:
            self._real = StorageRealService()
        return self._real.load(id)
