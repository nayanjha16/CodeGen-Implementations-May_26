"""DesignPatternsSolid | kind=design_pattern | label=command | domain=sync | tier=logging"""
from __future__ import annotations

from abc import ABC, abstractmethod

class SyncCommand(ABC):
    @abstractmethod
    def execute(self) -> str: ...

class SyncReceiver:
    def action(self, x: str) -> str:
        return f"done-sync:{x}"

class SyncActionCommand(SyncCommand):
    def __init__(self, receiver: SyncReceiver, payload: str) -> None:
        self.receiver = receiver
        self.payload = payload

    def execute(self) -> str:
        return self.receiver.action(self.payload)
