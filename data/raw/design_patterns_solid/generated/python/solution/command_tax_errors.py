"""DesignPatternsSolid | kind=design_pattern | label=command | domain=tax | tier=errors"""
from __future__ import annotations

from abc import ABC, abstractmethod

class TaxCommand(ABC):
    @abstractmethod
    def execute(self) -> str: ...

class TaxReceiver:
    def action(self, x: str) -> str:
        return f"done-tax:{x}"

class TaxActionCommand(TaxCommand):
    def __init__(self, receiver: TaxReceiver, payload: str) -> None:
        self.receiver = receiver
        self.payload = payload

    def execute(self) -> str:
        return self.receiver.action(self.payload)
