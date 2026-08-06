"""DesignPatternsSolid | kind=design_pattern | label=command | domain=config | tier=errors"""
from __future__ import annotations

from abc import ABC, abstractmethod

class ConfigCommand(ABC):
    @abstractmethod
    def execute(self) -> str: ...

class ConfigReceiver:
    def action(self, x: str) -> str:
        return f"done-config:{x}"

class ConfigActionCommand(ConfigCommand):
    def __init__(self, receiver: ConfigReceiver, payload: str) -> None:
        self.receiver = receiver
        self.payload = payload

    def execute(self) -> str:
        return self.receiver.action(self.payload)
