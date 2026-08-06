"""DesignPatternsSolid | kind=design_pattern | label=command | domain=plugin | tier=logging"""
from __future__ import annotations

from abc import ABC, abstractmethod

class PluginCommand(ABC):
    @abstractmethod
    def execute(self) -> str: ...

class PluginReceiver:
    def action(self, x: str) -> str:
        return f"done-plugin:{x}"

class PluginActionCommand(PluginCommand):
    def __init__(self, receiver: PluginReceiver, payload: str) -> None:
        self.receiver = receiver
        self.payload = payload

    def execute(self) -> str:
        return self.receiver.action(self.payload)
