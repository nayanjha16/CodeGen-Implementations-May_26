"""DesignPatternsSolid | kind=design_pattern | label=command | domain=game | tier=errors"""
from __future__ import annotations

from abc import ABC, abstractmethod

class GameCommand(ABC):
    @abstractmethod
    def execute(self) -> str: ...

class GameReceiver:
    def action(self, x: str) -> str:
        return f"done-game:{x}"

class GameActionCommand(GameCommand):
    def __init__(self, receiver: GameReceiver, payload: str) -> None:
        self.receiver = receiver
        self.payload = payload

    def execute(self) -> str:
        return self.receiver.action(self.payload)
