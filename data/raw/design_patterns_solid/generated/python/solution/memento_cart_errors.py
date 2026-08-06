"""DesignPatternsSolid | kind=design_pattern | label=memento | domain=cart | tier=errors"""
from __future__ import annotations

from dataclasses import dataclass

@dataclass(frozen=True)
class CartMemento:
    state: str

class CartOriginator:
    def __init__(self) -> None:
        self.state = "cart-init"

    def set_state(self, state: str) -> None:
        self.state = state

    def get_state(self) -> str:
        return self.state

    def save(self) -> CartMemento:
        return CartMemento(self.state)

    def restore(self, m: CartMemento) -> None:
        self.state = m.state
