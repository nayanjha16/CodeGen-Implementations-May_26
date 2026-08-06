"""DesignPatternsSolid | kind=design_pattern | label=state | domain=report | tier=errors"""
from __future__ import annotations

from __future__ import annotations
from abc import ABC, abstractmethod

class ReportState(ABC):
    @abstractmethod
    def handle(self, ctx: "ReportContext") -> str: ...

class ReportOnState(ReportState):
    def handle(self, ctx: "ReportContext") -> str:
        ctx.set_state(ReportOffState())
        return "was-on-report"

class ReportOffState(ReportState):
    def handle(self, ctx: "ReportContext") -> str:
        ctx.set_state(ReportOnState())
        return "was-off-report"

class ReportContext:
    def __init__(self) -> None:
        self.state: ReportState = ReportOffState()

    def set_state(self, state: ReportState) -> None:
        self.state = state

    def request(self) -> str:
        return self.state.handle(self)
