"""DesignPatternsSolid | kind=design_pattern | label=memento | domain=editor | tier=minimal"""
from __future__ import annotations

from dataclasses import dataclass

@dataclass(frozen=True)
class EditorMemento:
    state: str

class EditorOriginator:
    def __init__(self) -> None:
        self.state = "editor-init"

    def set_state(self, state: str) -> None:
        self.state = state

    def get_state(self) -> str:
        return self.state

    def save(self) -> EditorMemento:
        return EditorMemento(self.state)

    def restore(self, m: EditorMemento) -> None:
        self.state = m.state
