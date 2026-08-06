"""DesignPatternsSolid | kind=design_pattern | label=memento | domain=game | tier=minimal"""
from __future__ import annotations

from dataclasses import dataclass

@dataclass(frozen=True)
class GameMemento:
    state: str

class GameOriginator:
    def __init__(self) -> None:
        self.state = "game-init"

    def set_state(self, state: str) -> None:
        self.state = state

    def get_state(self) -> str:
        return self.state

    def save(self) -> GameMemento:
        return GameMemento(self.state)

    def restore(self, m: GameMemento) -> None:
        self.state = m.state
