"""DesignPatternsSolid | kind=design_pattern | label=state | domain=billing | tier=minimal"""
from __future__ import annotations

from __future__ import annotations
from abc import ABC, abstractmethod

class BillingState(ABC):
    @abstractmethod
    def handle(self, ctx: "BillingContext") -> str: ...

class BillingOnState(BillingState):
    def handle(self, ctx: "BillingContext") -> str:
        ctx.set_state(BillingOffState())
        return "was-on-billing"

class BillingOffState(BillingState):
    def handle(self, ctx: "BillingContext") -> str:
        ctx.set_state(BillingOnState())
        return "was-off-billing"

class BillingContext:
    def __init__(self) -> None:
        self.state: BillingState = BillingOffState()

    def set_state(self, state: BillingState) -> None:
        self.state = state

    def request(self) -> str:
        return self.state.handle(self)
