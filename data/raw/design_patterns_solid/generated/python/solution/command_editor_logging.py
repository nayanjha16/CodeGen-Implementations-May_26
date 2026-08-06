"""DesignPatternsSolid | kind=design_pattern | label=command | domain=editor | tier=logging"""
from __future__ import annotations

from abc import ABC, abstractmethod

class EditorCommand(ABC):
    @abstractmethod
    def execute(self) -> str: ...

class EditorReceiver:
    def action(self, x: str) -> str:
        return f"done-editor:{x}"

class EditorActionCommand(EditorCommand):
    def __init__(self, receiver: EditorReceiver, payload: str) -> None:
        self.receiver = receiver
        self.payload = payload

    def execute(self) -> str:
        return self.receiver.action(self.payload)
