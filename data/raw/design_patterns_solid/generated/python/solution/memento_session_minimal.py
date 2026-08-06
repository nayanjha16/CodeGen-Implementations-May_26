"""DesignPatternsSolid | kind=design_pattern | label=memento | domain=session | tier=minimal"""
from __future__ import annotations

from dataclasses import dataclass

@dataclass(frozen=True)
class SessionMemento:
    state: str

class SessionOriginator:
    def __init__(self) -> None:
        self.state = "session-init"

    def set_state(self, state: str) -> None:
        self.state = state

    def get_state(self) -> str:
        return self.state

    def save(self) -> SessionMemento:
        return SessionMemento(self.state)

    def restore(self, m: SessionMemento) -> None:
        self.state = m.state
