"""DesignPatternsSolid | kind=design_pattern | label=command | domain=metrics | tier=errors"""
from __future__ import annotations

from abc import ABC, abstractmethod

class MetricsCommand(ABC):
    @abstractmethod
    def execute(self) -> str: ...

class MetricsReceiver:
    def action(self, x: str) -> str:
        return f"done-metrics:{x}"

class MetricsActionCommand(MetricsCommand):
    def __init__(self, receiver: MetricsReceiver, payload: str) -> None:
        self.receiver = receiver
        self.payload = payload

    def execute(self) -> str:
        return self.receiver.action(self.payload)
