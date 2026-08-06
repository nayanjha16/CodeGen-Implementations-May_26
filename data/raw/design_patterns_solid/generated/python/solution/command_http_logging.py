"""DesignPatternsSolid | kind=design_pattern | label=command | domain=http | tier=logging"""
from __future__ import annotations

from abc import ABC, abstractmethod

class HttpCommand(ABC):
    @abstractmethod
    def execute(self) -> str: ...

class HttpReceiver:
    def action(self, x: str) -> str:
        return f"done-http:{x}"

class HttpActionCommand(HttpCommand):
    def __init__(self, receiver: HttpReceiver, payload: str) -> None:
        self.receiver = receiver
        self.payload = payload

    def execute(self) -> str:
        return self.receiver.action(self.payload)
