"""DesignPatternsSolid | kind=design_pattern | label=command | domain=sensors | tier=errors"""
from __future__ import annotations

from abc import ABC, abstractmethod

class SensorsCommand(ABC):
    @abstractmethod
    def execute(self) -> str: ...

class SensorsReceiver:
    def action(self, x: str) -> str:
        return f"done-sensors:{x}"

class SensorsActionCommand(SensorsCommand):
    def __init__(self, receiver: SensorsReceiver, payload: str) -> None:
        self.receiver = receiver
        self.payload = payload

    def execute(self) -> str:
        return self.receiver.action(self.payload)
