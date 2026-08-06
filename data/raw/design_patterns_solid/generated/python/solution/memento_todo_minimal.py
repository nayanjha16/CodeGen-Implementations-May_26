"""DesignPatternsSolid | kind=design_pattern | label=memento | domain=todo | tier=minimal"""
from __future__ import annotations

from dataclasses import dataclass

@dataclass(frozen=True)
class TodoMemento:
    state: str

class TodoOriginator:
    def __init__(self) -> None:
        self.state = "todo-init"

    def set_state(self, state: str) -> None:
        self.state = state

    def get_state(self) -> str:
        return self.state

    def save(self) -> TodoMemento:
        return TodoMemento(self.state)

    def restore(self, m: TodoMemento) -> None:
        self.state = m.state
