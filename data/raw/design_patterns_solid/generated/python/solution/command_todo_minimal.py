"""DesignPatternsSolid | kind=design_pattern | label=command | domain=todo | tier=minimal"""
from __future__ import annotations

from abc import ABC, abstractmethod

class TodoCommand(ABC):
    @abstractmethod
    def execute(self) -> str: ...

class TodoReceiver:
    def action(self, x: str) -> str:
        return f"done-todo:{x}"

class TodoActionCommand(TodoCommand):
    def __init__(self, receiver: TodoReceiver, payload: str) -> None:
        self.receiver = receiver
        self.payload = payload

    def execute(self) -> str:
        return self.receiver.action(self.payload)
