"""DesignPatternsSolid | kind=design_pattern | label=command | domain=notes | tier=logging"""
from __future__ import annotations

from abc import ABC, abstractmethod

class NotesCommand(ABC):
    @abstractmethod
    def execute(self) -> str: ...

class NotesReceiver:
    def action(self, x: str) -> str:
        return f"done-notes:{x}"

class NotesActionCommand(NotesCommand):
    def __init__(self, receiver: NotesReceiver, payload: str) -> None:
        self.receiver = receiver
        self.payload = payload

    def execute(self) -> str:
        return self.receiver.action(self.payload)
