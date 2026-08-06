"""DesignPatternsSolid | kind=design_pattern | label=memento | domain=discount | tier=errors"""
from __future__ import annotations

from dataclasses import dataclass

@dataclass(frozen=True)
class DiscountMemento:
    state: str

class DiscountOriginator:
    def __init__(self) -> None:
        self.state = "discount-init"

    def set_state(self, state: str) -> None:
        self.state = state

    def get_state(self) -> str:
        return self.state

    def save(self) -> DiscountMemento:
        return DiscountMemento(self.state)

    def restore(self, m: DiscountMemento) -> None:
        self.state = m.state
