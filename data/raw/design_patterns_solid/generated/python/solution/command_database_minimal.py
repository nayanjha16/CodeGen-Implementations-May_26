"""DesignPatternsSolid | kind=design_pattern | label=command | domain=database | tier=minimal"""
from __future__ import annotations

from abc import ABC, abstractmethod

class DatabaseCommand(ABC):
    @abstractmethod
    def execute(self) -> str: ...

class DatabaseReceiver:
    def action(self, x: str) -> str:
        return f"done-database:{x}"

class DatabaseActionCommand(DatabaseCommand):
    def __init__(self, receiver: DatabaseReceiver, payload: str) -> None:
        self.receiver = receiver
        self.payload = payload

    def execute(self) -> str:
        return self.receiver.action(self.payload)
