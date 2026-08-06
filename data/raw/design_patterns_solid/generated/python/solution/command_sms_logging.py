"""DesignPatternsSolid | kind=design_pattern | label=command | domain=sms | tier=logging"""
from __future__ import annotations

from abc import ABC, abstractmethod

class SmsCommand(ABC):
    @abstractmethod
    def execute(self) -> str: ...

class SmsReceiver:
    def action(self, x: str) -> str:
        return f"done-sms:{x}"

class SmsActionCommand(SmsCommand):
    def __init__(self, receiver: SmsReceiver, payload: str) -> None:
        self.receiver = receiver
        self.payload = payload

    def execute(self) -> str:
        return self.receiver.action(self.payload)
