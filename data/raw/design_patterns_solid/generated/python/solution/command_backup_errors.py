"""DesignPatternsSolid | kind=design_pattern | label=command | domain=backup | tier=errors"""
from __future__ import annotations

from abc import ABC, abstractmethod

class BackupCommand(ABC):
    @abstractmethod
    def execute(self) -> str: ...

class BackupReceiver:
    def action(self, x: str) -> str:
        return f"done-backup:{x}"

class BackupActionCommand(BackupCommand):
    def __init__(self, receiver: BackupReceiver, payload: str) -> None:
        self.receiver = receiver
        self.payload = payload

    def execute(self) -> str:
        return self.receiver.action(self.payload)
