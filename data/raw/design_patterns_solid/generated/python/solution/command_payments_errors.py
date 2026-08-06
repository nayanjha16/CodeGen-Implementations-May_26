"""DesignPatternsSolid | kind=design_pattern | label=command | domain=payments | tier=errors"""
from __future__ import annotations

from abc import ABC, abstractmethod

class PaymentsCommand(ABC):
    @abstractmethod
    def execute(self) -> str: ...

class PaymentsReceiver:
    def action(self, x: str) -> str:
        return f"done-payments:{x}"

class PaymentsActionCommand(PaymentsCommand):
    def __init__(self, receiver: PaymentsReceiver, payload: str) -> None:
        self.receiver = receiver
        self.payload = payload

    def execute(self) -> str:
        return self.receiver.action(self.payload)
