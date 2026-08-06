"""DesignPatternsSolid | kind=design_pattern | label=command | domain=review | tier=logging"""
from __future__ import annotations

from abc import ABC, abstractmethod

class ReviewCommand(ABC):
    @abstractmethod
    def execute(self) -> str: ...

class ReviewReceiver:
    def action(self, x: str) -> str:
        return f"done-review:{x}"

class ReviewActionCommand(ReviewCommand):
    def __init__(self, receiver: ReviewReceiver, payload: str) -> None:
        self.receiver = receiver
        self.payload = payload

    def execute(self) -> str:
        return self.receiver.action(self.payload)
