"""DesignPatternsSolid | kind=design_pattern | label=command | domain=calendar | tier=logging"""
from __future__ import annotations

from abc import ABC, abstractmethod

class CalendarCommand(ABC):
    @abstractmethod
    def execute(self) -> str: ...

class CalendarReceiver:
    def action(self, x: str) -> str:
        return f"done-calendar:{x}"

class CalendarActionCommand(CalendarCommand):
    def __init__(self, receiver: CalendarReceiver, payload: str) -> None:
        self.receiver = receiver
        self.payload = payload

    def execute(self) -> str:
        return self.receiver.action(self.payload)
