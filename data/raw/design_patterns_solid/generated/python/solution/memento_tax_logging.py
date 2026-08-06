"""DesignPatternsSolid | kind=design_pattern | label=memento | domain=tax | tier=logging"""
from __future__ import annotations

from dataclasses import dataclass

@dataclass(frozen=True)
class TaxMemento:
    state: str

class TaxOriginator:
    def __init__(self) -> None:
        self.state = "tax-init"

    def set_state(self, state: str) -> None:
        self.state = state

    def get_state(self) -> str:
        return self.state

    def save(self) -> TaxMemento:
        return TaxMemento(self.state)

    def restore(self, m: TaxMemento) -> None:
        self.state = m.state
