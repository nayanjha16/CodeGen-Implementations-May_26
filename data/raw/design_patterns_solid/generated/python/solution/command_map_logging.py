"""DesignPatternsSolid | kind=design_pattern | label=command | domain=map | tier=logging"""
from __future__ import annotations

from abc import ABC, abstractmethod

class MapCommand(ABC):
    @abstractmethod
    def execute(self) -> str: ...

class MapReceiver:
    def action(self, x: str) -> str:
        return f"done-map:{x}"

class MapActionCommand(MapCommand):
    def __init__(self, receiver: MapReceiver, payload: str) -> None:
        self.receiver = receiver
        self.payload = payload

    def execute(self) -> str:
        return self.receiver.action(self.payload)
