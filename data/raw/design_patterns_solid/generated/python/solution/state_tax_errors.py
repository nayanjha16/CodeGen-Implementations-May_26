"""DesignPatternsSolid | kind=design_pattern | label=state | domain=tax | tier=errors"""
from __future__ import annotations

from __future__ import annotations
from abc import ABC, abstractmethod

class TaxState(ABC):
    @abstractmethod
    def handle(self, ctx: "TaxContext") -> str: ...

class TaxOnState(TaxState):
    def handle(self, ctx: "TaxContext") -> str:
        ctx.set_state(TaxOffState())
        return "was-on-tax"

class TaxOffState(TaxState):
    def handle(self, ctx: "TaxContext") -> str:
        ctx.set_state(TaxOnState())
        return "was-off-tax"

class TaxContext:
    def __init__(self) -> None:
        self.state: TaxState = TaxOffState()

    def set_state(self, state: TaxState) -> None:
        self.state = state

    def request(self) -> str:
        return self.state.handle(self)
