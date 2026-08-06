"""DesignPatternsSolid | kind=design_pattern | label=command | domain=discount | tier=logging"""
from __future__ import annotations

from abc import ABC, abstractmethod

class DiscountCommand(ABC):
    @abstractmethod
    def execute(self) -> str: ...

class DiscountReceiver:
    def action(self, x: str) -> str:
        return f"done-discount:{x}"

class DiscountActionCommand(DiscountCommand):
    def __init__(self, receiver: DiscountReceiver, payload: str) -> None:
        self.receiver = receiver
        self.payload = payload

    def execute(self) -> str:
        return self.receiver.action(self.payload)
