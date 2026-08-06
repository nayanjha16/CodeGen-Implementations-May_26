"""DesignPatternsSolid | kind=design_pattern | label=memento | domain=database | tier=logging"""
from __future__ import annotations

from dataclasses import dataclass

@dataclass(frozen=True)
class DatabaseMemento:
    state: str

class DatabaseOriginator:
    def __init__(self) -> None:
        self.state = "database-init"

    def set_state(self, state: str) -> None:
        self.state = state

    def get_state(self) -> str:
        return self.state

    def save(self) -> DatabaseMemento:
        return DatabaseMemento(self.state)

    def restore(self, m: DatabaseMemento) -> None:
        self.state = m.state
