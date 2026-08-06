"""DesignPatternsSolid | kind=design_pattern | label=memento | domain=email | tier=logging"""
from __future__ import annotations

from dataclasses import dataclass

@dataclass(frozen=True)
class EmailMemento:
    state: str

class EmailOriginator:
    def __init__(self) -> None:
        self.state = "email-init"

    def set_state(self, state: str) -> None:
        self.state = state

    def get_state(self) -> str:
        return self.state

    def save(self) -> EmailMemento:
        return EmailMemento(self.state)

    def restore(self, m: EmailMemento) -> None:
        self.state = m.state
