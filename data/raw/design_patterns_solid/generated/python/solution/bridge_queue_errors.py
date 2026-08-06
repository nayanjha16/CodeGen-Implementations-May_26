"""DesignPatternsSolid | kind=design_pattern | label=bridge | domain=queue | tier=errors"""
from __future__ import annotations

from abc import ABC, abstractmethod

class QueueImpl(ABC):
    @abstractmethod
    def write(self, msg: str) -> str: ...

class QueueFileImpl(QueueImpl):
    def write(self, msg: str) -> str:
        return f"file:queue:{msg}"

class QueueMemoryImpl(QueueImpl):
    def write(self, msg: str) -> str:
        return f"mem:queue:{msg}"

class QueueBridge(ABC):
    def __init__(self, impl: QueueImpl) -> None:
        self.impl = impl

    @abstractmethod
    def send(self, msg: str) -> str: ...

class QueueAlertBridge(QueueBridge):
    def send(self, msg: str) -> str:
        return self.impl.write("ALERT-" + msg)
