"""DesignPatternsSolid | kind=design_pattern | label=command | domain=email | tier=minimal"""
from __future__ import annotations

from abc import ABC, abstractmethod

class EmailCommand(ABC):
    @abstractmethod
    def execute(self) -> str: ...

class EmailReceiver:
    def action(self, x: str) -> str:
        return f"done-email:{x}"

class EmailActionCommand(EmailCommand):
    def __init__(self, receiver: EmailReceiver, payload: str) -> None:
        self.receiver = receiver
        self.payload = payload

    def execute(self) -> str:
        return self.receiver.action(self.payload)
