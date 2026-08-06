"""DesignPatternsSolid | kind=design_pattern | label=command | domain=queue | tier=errors"""
from __future__ import annotations

from abc import ABC, abstractmethod

class QueueCommand(ABC):
    @abstractmethod
    def execute(self) -> str: ...

class QueueReceiver:
    def action(self, x: str) -> str:
        return f"done-queue:{x}"

class QueueActionCommand(QueueCommand):
    def __init__(self, receiver: QueueReceiver, payload: str) -> None:
        self.receiver = receiver
        self.payload = payload

    def execute(self) -> str:
        return self.receiver.action(self.payload)
