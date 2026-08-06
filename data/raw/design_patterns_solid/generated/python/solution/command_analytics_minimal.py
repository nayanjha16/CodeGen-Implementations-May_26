"""DesignPatternsSolid | kind=design_pattern | label=command | domain=analytics | tier=minimal"""
from __future__ import annotations

from abc import ABC, abstractmethod

class AnalyticsCommand(ABC):
    @abstractmethod
    def execute(self) -> str: ...

class AnalyticsReceiver:
    def action(self, x: str) -> str:
        return f"done-analytics:{x}"

class AnalyticsActionCommand(AnalyticsCommand):
    def __init__(self, receiver: AnalyticsReceiver, payload: str) -> None:
        self.receiver = receiver
        self.payload = payload

    def execute(self) -> str:
        return self.receiver.action(self.payload)
