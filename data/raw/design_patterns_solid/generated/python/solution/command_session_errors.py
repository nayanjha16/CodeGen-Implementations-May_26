"""DesignPatternsSolid | kind=design_pattern | label=command | domain=session | tier=errors"""
from __future__ import annotations

from abc import ABC, abstractmethod

class SessionCommand(ABC):
    @abstractmethod
    def execute(self) -> str: ...

class SessionReceiver:
    def action(self, x: str) -> str:
        return f"done-session:{x}"

class SessionActionCommand(SessionCommand):
    def __init__(self, receiver: SessionReceiver, payload: str) -> None:
        self.receiver = receiver
        self.payload = payload

    def execute(self) -> str:
        return self.receiver.action(self.payload)
