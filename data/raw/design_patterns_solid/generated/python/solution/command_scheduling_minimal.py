"""DesignPatternsSolid | kind=design_pattern | label=command | domain=scheduling | tier=minimal"""
from __future__ import annotations

from abc import ABC, abstractmethod

class SchedulingCommand(ABC):
    @abstractmethod
    def execute(self) -> str: ...

class SchedulingReceiver:
    def action(self, x: str) -> str:
        return f"done-scheduling:{x}"

class SchedulingActionCommand(SchedulingCommand):
    def __init__(self, receiver: SchedulingReceiver, payload: str) -> None:
        self.receiver = receiver
        self.payload = payload

    def execute(self) -> str:
        return self.receiver.action(self.payload)
