"""DesignPatternsSolid | kind=design_pattern | label=command | domain=ticket | tier=minimal"""
from __future__ import annotations

from abc import ABC, abstractmethod

class TicketCommand(ABC):
    @abstractmethod
    def execute(self) -> str: ...

class TicketReceiver:
    def action(self, x: str) -> str:
        return f"done-ticket:{x}"

class TicketActionCommand(TicketCommand):
    def __init__(self, receiver: TicketReceiver, payload: str) -> None:
        self.receiver = receiver
        self.payload = payload

    def execute(self) -> str:
        return self.receiver.action(self.payload)
