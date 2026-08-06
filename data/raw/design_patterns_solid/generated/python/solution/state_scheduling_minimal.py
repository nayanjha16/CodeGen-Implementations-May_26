"""DesignPatternsSolid | kind=design_pattern | label=state | domain=scheduling | tier=minimal"""
from __future__ import annotations

from __future__ import annotations
from abc import ABC, abstractmethod

class SchedulingState(ABC):
    @abstractmethod
    def handle(self, ctx: "SchedulingContext") -> str: ...

class SchedulingOnState(SchedulingState):
    def handle(self, ctx: "SchedulingContext") -> str:
        ctx.set_state(SchedulingOffState())
        return "was-on-scheduling"

class SchedulingOffState(SchedulingState):
    def handle(self, ctx: "SchedulingContext") -> str:
        ctx.set_state(SchedulingOnState())
        return "was-off-scheduling"

class SchedulingContext:
    def __init__(self) -> None:
        self.state: SchedulingState = SchedulingOffState()

    def set_state(self, state: SchedulingState) -> None:
        self.state = state

    def request(self) -> str:
        return self.state.handle(self)
