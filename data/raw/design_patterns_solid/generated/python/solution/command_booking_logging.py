"""DesignPatternsSolid | kind=design_pattern | label=command | domain=booking | tier=logging"""
from __future__ import annotations

from abc import ABC, abstractmethod

class BookingCommand(ABC):
    @abstractmethod
    def execute(self) -> str: ...

class BookingReceiver:
    def action(self, x: str) -> str:
        return f"done-booking:{x}"

class BookingActionCommand(BookingCommand):
    def __init__(self, receiver: BookingReceiver, payload: str) -> None:
        self.receiver = receiver
        self.payload = payload

    def execute(self) -> str:
        return self.receiver.action(self.payload)
