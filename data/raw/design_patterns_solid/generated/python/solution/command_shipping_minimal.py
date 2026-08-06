"""DesignPatternsSolid | kind=design_pattern | label=command | domain=shipping | tier=minimal"""
from __future__ import annotations

from abc import ABC, abstractmethod

class ShippingCommand(ABC):
    @abstractmethod
    def execute(self) -> str: ...

class ShippingReceiver:
    def action(self, x: str) -> str:
        return f"done-shipping:{x}"

class ShippingActionCommand(ShippingCommand):
    def __init__(self, receiver: ShippingReceiver, payload: str) -> None:
        self.receiver = receiver
        self.payload = payload

    def execute(self) -> str:
        return self.receiver.action(self.payload)
