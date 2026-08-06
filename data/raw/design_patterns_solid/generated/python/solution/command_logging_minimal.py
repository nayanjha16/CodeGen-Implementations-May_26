"""DesignPatternsSolid | kind=design_pattern | label=command | domain=logging | tier=minimal"""
from __future__ import annotations

from abc import ABC, abstractmethod

class LoggingCommand(ABC):
    @abstractmethod
    def execute(self) -> str: ...

class LoggingReceiver:
    def action(self, x: str) -> str:
        return f"done-logging:{x}"

class LoggingActionCommand(LoggingCommand):
    def __init__(self, receiver: LoggingReceiver, payload: str) -> None:
        self.receiver = receiver
        self.payload = payload

    def execute(self) -> str:
        return self.receiver.action(self.payload)
