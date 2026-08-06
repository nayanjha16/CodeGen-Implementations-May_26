"""DesignPatternsSolid | kind=design_pattern | label=state | domain=sensors | tier=errors"""
from __future__ import annotations

from __future__ import annotations
from abc import ABC, abstractmethod

class SensorsState(ABC):
    @abstractmethod
    def handle(self, ctx: "SensorsContext") -> str: ...

class SensorsOnState(SensorsState):
    def handle(self, ctx: "SensorsContext") -> str:
        ctx.set_state(SensorsOffState())
        return "was-on-sensors"

class SensorsOffState(SensorsState):
    def handle(self, ctx: "SensorsContext") -> str:
        ctx.set_state(SensorsOnState())
        return "was-off-sensors"

class SensorsContext:
    def __init__(self) -> None:
        self.state: SensorsState = SensorsOffState()

    def set_state(self, state: SensorsState) -> None:
        self.state = state

    def request(self) -> str:
        return self.state.handle(self)
