"""DesignPatternsSolid | kind=design_pattern | label=memento | domain=analytics | tier=minimal"""
from __future__ import annotations

from dataclasses import dataclass

@dataclass(frozen=True)
class AnalyticsMemento:
    state: str

class AnalyticsOriginator:
    def __init__(self) -> None:
        self.state = "analytics-init"

    def set_state(self, state: str) -> None:
        self.state = state

    def get_state(self) -> str:
        return self.state

    def save(self) -> AnalyticsMemento:
        return AnalyticsMemento(self.state)

    def restore(self, m: AnalyticsMemento) -> None:
        self.state = m.state
