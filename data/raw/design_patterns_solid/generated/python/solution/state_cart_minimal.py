"""DesignPatternsSolid | kind=design_pattern | label=state | domain=cart | tier=minimal"""
from __future__ import annotations

from __future__ import annotations
from abc import ABC, abstractmethod

class CartState(ABC):
    @abstractmethod
    def handle(self, ctx: "CartContext") -> str: ...

class CartOnState(CartState):
    def handle(self, ctx: "CartContext") -> str:
        ctx.set_state(CartOffState())
        return "was-on-cart"

class CartOffState(CartState):
    def handle(self, ctx: "CartContext") -> str:
        ctx.set_state(CartOnState())
        return "was-off-cart"

class CartContext:
    def __init__(self) -> None:
        self.state: CartState = CartOffState()

    def set_state(self, state: CartState) -> None:
        self.state = state

    def request(self) -> str:
        return self.state.handle(self)
