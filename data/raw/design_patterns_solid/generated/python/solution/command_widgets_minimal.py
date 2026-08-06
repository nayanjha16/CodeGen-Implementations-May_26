"""DesignPatternsSolid | kind=design_pattern | label=command | domain=widgets | tier=minimal"""
from __future__ import annotations

from abc import ABC, abstractmethod

class WidgetsCommand(ABC):
    @abstractmethod
    def execute(self) -> str: ...

class WidgetsReceiver:
    def action(self, x: str) -> str:
        return f"done-widgets:{x}"

class WidgetsActionCommand(WidgetsCommand):
    def __init__(self, receiver: WidgetsReceiver, payload: str) -> None:
        self.receiver = receiver
        self.payload = payload

    def execute(self) -> str:
        return self.receiver.action(self.payload)
