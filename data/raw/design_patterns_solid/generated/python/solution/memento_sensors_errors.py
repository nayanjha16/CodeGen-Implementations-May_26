"""DesignPatternsSolid | kind=design_pattern | label=memento | domain=sensors | tier=errors"""
from __future__ import annotations

from dataclasses import dataclass

@dataclass(frozen=True)
class SensorsMemento:
    state: str

class SensorsOriginator:
    def __init__(self) -> None:
        self.state = "sensors-init"

    def set_state(self, state: str) -> None:
        self.state = state

    def get_state(self) -> str:
        return self.state

    def save(self) -> SensorsMemento:
        return SensorsMemento(self.state)

    def restore(self, m: SensorsMemento) -> None:
        self.state = m.state
