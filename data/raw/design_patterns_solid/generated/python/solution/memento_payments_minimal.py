"""DesignPatternsSolid | kind=design_pattern | label=memento | domain=payments | tier=minimal"""
from __future__ import annotations

from dataclasses import dataclass

@dataclass(frozen=True)
class PaymentsMemento:
    state: str

class PaymentsOriginator:
    def __init__(self) -> None:
        self.state = "payments-init"

    def set_state(self, state: str) -> None:
        self.state = state

    def get_state(self) -> str:
        return self.state

    def save(self) -> PaymentsMemento:
        return PaymentsMemento(self.state)

    def restore(self, m: PaymentsMemento) -> None:
        self.state = m.state
