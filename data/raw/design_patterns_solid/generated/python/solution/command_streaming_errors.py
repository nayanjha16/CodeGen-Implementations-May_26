"""DesignPatternsSolid | kind=design_pattern | label=command | domain=streaming | tier=errors"""
from __future__ import annotations

from abc import ABC, abstractmethod

class StreamingCommand(ABC):
    @abstractmethod
    def execute(self) -> str: ...

class StreamingReceiver:
    def action(self, x: str) -> str:
        return f"done-streaming:{x}"

class StreamingActionCommand(StreamingCommand):
    def __init__(self, receiver: StreamingReceiver, payload: str) -> None:
        self.receiver = receiver
        self.payload = payload

    def execute(self) -> str:
        return self.receiver.action(self.payload)
