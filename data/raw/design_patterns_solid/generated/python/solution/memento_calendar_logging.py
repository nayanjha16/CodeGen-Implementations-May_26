"""DesignPatternsSolid | kind=design_pattern | label=memento | domain=calendar | tier=logging"""
from __future__ import annotations

from dataclasses import dataclass

@dataclass(frozen=True)
class CalendarMemento:
    state: str

class CalendarOriginator:
    def __init__(self) -> None:
        self.state = "calendar-init"

    def set_state(self, state: str) -> None:
        self.state = state

    def get_state(self) -> str:
        return self.state

    def save(self) -> CalendarMemento:
        return CalendarMemento(self.state)

    def restore(self, m: CalendarMemento) -> None:
        self.state = m.state
