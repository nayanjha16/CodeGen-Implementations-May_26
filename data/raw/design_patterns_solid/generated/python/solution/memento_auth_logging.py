"""DesignPatternsSolid | kind=design_pattern | label=memento | domain=auth | tier=logging"""
from __future__ import annotations

from dataclasses import dataclass

@dataclass(frozen=True)
class AuthMemento:
    state: str

class AuthOriginator:
    def __init__(self) -> None:
        self.state = "auth-init"

    def set_state(self, state: str) -> None:
        self.state = state

    def get_state(self) -> str:
        return self.state

    def save(self) -> AuthMemento:
        return AuthMemento(self.state)

    def restore(self, m: AuthMemento) -> None:
        self.state = m.state
