"""DesignPatternsSolid | kind=design_pattern | label=state | domain=metrics | tier=minimal"""
from __future__ import annotations

from __future__ import annotations
from abc import ABC, abstractmethod

class MetricsState(ABC):
    @abstractmethod
    def handle(self, ctx: "MetricsContext") -> str: ...

class MetricsOnState(MetricsState):
    def handle(self, ctx: "MetricsContext") -> str:
        ctx.set_state(MetricsOffState())
        return "was-on-metrics"

class MetricsOffState(MetricsState):
    def handle(self, ctx: "MetricsContext") -> str:
        ctx.set_state(MetricsOnState())
        return "was-off-metrics"

class MetricsContext:
    def __init__(self) -> None:
        self.state: MetricsState = MetricsOffState()

    def set_state(self, state: MetricsState) -> None:
        self.state = state

    def request(self) -> str:
        return self.state.handle(self)
