"""DesignPatternsSolid | kind=design_pattern | label=proxy | domain=backup | tier=errors"""
from __future__ import annotations

from abc import ABC, abstractmethod

class BackupService(ABC):
    @abstractmethod
    def load(self, id: str) -> str: ...

class BackupRealService(BackupService):
    def load(self, id: str) -> str:
        return f"real-backup:{id}"

class BackupProxy(BackupService):
    def __init__(self, allowed: bool) -> None:
        self.allowed = allowed
        self._real: BackupRealService | None = None

    def load(self, id: str) -> str:
        if not self.allowed:
            return "denied"
        if self._real is None:
            self._real = BackupRealService()
        return self._real.load(id)
