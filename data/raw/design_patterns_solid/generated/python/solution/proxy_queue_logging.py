"""DesignPatternsSolid | kind=design_pattern | label=proxy | domain=queue | tier=logging"""
from __future__ import annotations

from abc import ABC, abstractmethod

class QueueService(ABC):
    @abstractmethod
    def load(self, id: str) -> str: ...

class QueueRealService(QueueService):
    def load(self, id: str) -> str:
        return f"real-queue:{id}"

class QueueProxy(QueueService):
    def __init__(self, allowed: bool) -> None:
        self.allowed = allowed
        self._real: QueueRealService | None = None

    def load(self, id: str) -> str:
        if not self.allowed:
            return "denied"
        if self._real is None:
            self._real = QueueRealService()
        return self._real.load(id)
