"""DesignPatternsSolid | kind=design_pattern | label=memento | domain=notes | tier=logging"""
from __future__ import annotations

from dataclasses import dataclass

@dataclass(frozen=True)
class NotesMemento:
    state: str

class NotesOriginator:
    def __init__(self) -> None:
        self.state = "notes-init"

    def set_state(self, state: str) -> None:
        self.state = state

    def get_state(self) -> str:
        return self.state

    def save(self) -> NotesMemento:
        return NotesMemento(self.state)

    def restore(self, m: NotesMemento) -> None:
        self.state = m.state
