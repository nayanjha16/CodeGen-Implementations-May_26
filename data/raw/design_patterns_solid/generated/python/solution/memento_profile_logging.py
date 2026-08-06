"""DesignPatternsSolid | kind=design_pattern | label=memento | domain=profile | tier=logging"""
from __future__ import annotations

from dataclasses import dataclass

@dataclass(frozen=True)
class ProfileMemento:
    state: str

class ProfileOriginator:
    def __init__(self) -> None:
        self.state = "profile-init"

    def set_state(self, state: str) -> None:
        self.state = state

    def get_state(self) -> str:
        return self.state

    def save(self) -> ProfileMemento:
        return ProfileMemento(self.state)

    def restore(self, m: ProfileMemento) -> None:
        self.state = m.state
