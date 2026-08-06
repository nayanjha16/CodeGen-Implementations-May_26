"""DesignPatternsSolid | kind=design_pattern | label=memento | domain=canvas | tier=logging"""
from __future__ import annotations

from dataclasses import dataclass

@dataclass(frozen=True)
class CanvasMemento:
    state: str

class CanvasOriginator:
    def __init__(self) -> None:
        self.state = "canvas-init"

    def set_state(self, state: str) -> None:
        self.state = state

    def get_state(self) -> str:
        return self.state

    def save(self) -> CanvasMemento:
        return CanvasMemento(self.state)

    def restore(self, m: CanvasMemento) -> None:
        self.state = m.state
