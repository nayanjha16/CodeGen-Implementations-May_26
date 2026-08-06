"""DesignPatternsSolid | kind=design_pattern | label=memento | domain=billing | tier=logging"""
from __future__ import annotations

from dataclasses import dataclass

@dataclass(frozen=True)
class BillingMemento:
    state: str

class BillingOriginator:
    def __init__(self) -> None:
        self.state = "billing-init"

    def set_state(self, state: str) -> None:
        self.state = state

    def get_state(self) -> str:
        return self.state

    def save(self) -> BillingMemento:
        return BillingMemento(self.state)

    def restore(self, m: BillingMemento) -> None:
        self.state = m.state
