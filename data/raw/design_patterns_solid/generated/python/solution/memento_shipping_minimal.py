"""DesignPatternsSolid | kind=design_pattern | label=memento | domain=shipping | tier=minimal"""
from __future__ import annotations

from dataclasses import dataclass

@dataclass(frozen=True)
class ShippingMemento:
    state: str

class ShippingOriginator:
    def __init__(self) -> None:
        self.state = "shipping-init"

    def set_state(self, state: str) -> None:
        self.state = state

    def get_state(self) -> str:
        return self.state

    def save(self) -> ShippingMemento:
        return ShippingMemento(self.state)

    def restore(self, m: ShippingMemento) -> None:
        self.state = m.state
