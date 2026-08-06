"""DesignPatternsSolid | kind=design_pattern | label=command | domain=canvas | tier=minimal"""
from __future__ import annotations

from abc import ABC, abstractmethod

class CanvasCommand(ABC):
    @abstractmethod
    def execute(self) -> str: ...

class CanvasReceiver:
    def action(self, x: str) -> str:
        return f"done-canvas:{x}"

class CanvasActionCommand(CanvasCommand):
    def __init__(self, receiver: CanvasReceiver, payload: str) -> None:
        self.receiver = receiver
        self.payload = payload

    def execute(self) -> str:
        return self.receiver.action(self.payload)
