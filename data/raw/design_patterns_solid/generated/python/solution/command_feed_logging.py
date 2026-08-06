"""DesignPatternsSolid | kind=design_pattern | label=command | domain=feed | tier=logging"""
from __future__ import annotations

from abc import ABC, abstractmethod

class FeedCommand(ABC):
    @abstractmethod
    def execute(self) -> str: ...

class FeedReceiver:
    def action(self, x: str) -> str:
        return f"done-feed:{x}"

class FeedActionCommand(FeedCommand):
    def __init__(self, receiver: FeedReceiver, payload: str) -> None:
        self.receiver = receiver
        self.payload = payload

    def execute(self) -> str:
        return self.receiver.action(self.payload)
