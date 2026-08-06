"""DesignPatternsSolid | kind=design_pattern | label=state | domain=shipping | tier=logging"""
from __future__ import annotations

from __future__ import annotations
from abc import ABC, abstractmethod

class ShippingState(ABC):
    @abstractmethod
    def handle(self, ctx: "ShippingContext") -> str: ...

class ShippingOnState(ShippingState):
    def handle(self, ctx: "ShippingContext") -> str:
        ctx.set_state(ShippingOffState())
        return "was-on-shipping"

class ShippingOffState(ShippingState):
    def handle(self, ctx: "ShippingContext") -> str:
        ctx.set_state(ShippingOnState())
        return "was-off-shipping"

class ShippingContext:
    def __init__(self) -> None:
        self.state: ShippingState = ShippingOffState()

    def set_state(self, state: ShippingState) -> None:
        self.state = state

    def request(self) -> str:
        return self.state.handle(self)
