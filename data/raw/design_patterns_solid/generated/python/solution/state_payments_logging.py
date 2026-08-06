"""DesignPatternsSolid | kind=design_pattern | label=state | domain=payments | tier=logging"""
from __future__ import annotations

from __future__ import annotations
from abc import ABC, abstractmethod

class PaymentsState(ABC):
    @abstractmethod
    def handle(self, ctx: "PaymentsContext") -> str: ...

class PaymentsOnState(PaymentsState):
    def handle(self, ctx: "PaymentsContext") -> str:
        ctx.set_state(PaymentsOffState())
        return "was-on-payments"

class PaymentsOffState(PaymentsState):
    def handle(self, ctx: "PaymentsContext") -> str:
        ctx.set_state(PaymentsOnState())
        return "was-off-payments"

class PaymentsContext:
    def __init__(self) -> None:
        self.state: PaymentsState = PaymentsOffState()

    def set_state(self, state: PaymentsState) -> None:
        self.state = state

    def request(self) -> str:
        return self.state.handle(self)
