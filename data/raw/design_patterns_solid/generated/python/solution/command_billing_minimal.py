"""DesignPatternsSolid | kind=design_pattern | label=command | domain=billing | tier=minimal"""
from __future__ import annotations

from abc import ABC, abstractmethod

class BillingCommand(ABC):
    @abstractmethod
    def execute(self) -> str: ...

class BillingReceiver:
    def action(self, x: str) -> str:
        return f"done-billing:{x}"

class BillingActionCommand(BillingCommand):
    def __init__(self, receiver: BillingReceiver, payload: str) -> None:
        self.receiver = receiver
        self.payload = payload

    def execute(self) -> str:
        return self.receiver.action(self.payload)
