"""DesignPatternsSolid | kind=design_pattern | label=command | domain=notifications | tier=logging"""
from __future__ import annotations

from abc import ABC, abstractmethod

class NotificationsCommand(ABC):
    @abstractmethod
    def execute(self) -> str: ...

class NotificationsReceiver:
    def action(self, x: str) -> str:
        return f"done-notifications:{x}"

class NotificationsActionCommand(NotificationsCommand):
    def __init__(self, receiver: NotificationsReceiver, payload: str) -> None:
        self.receiver = receiver
        self.payload = payload

    def execute(self) -> str:
        return self.receiver.action(self.payload)
