"""DesignPatternsSolid | kind=design_pattern | label=command | domain=search | tier=errors"""
from __future__ import annotations

from abc import ABC, abstractmethod

class SearchCommand(ABC):
    @abstractmethod
    def execute(self) -> str: ...

class SearchReceiver:
    def action(self, x: str) -> str:
        return f"done-search:{x}"

class SearchActionCommand(SearchCommand):
    def __init__(self, receiver: SearchReceiver, payload: str) -> None:
        self.receiver = receiver
        self.payload = payload

    def execute(self) -> str:
        return self.receiver.action(self.payload)
