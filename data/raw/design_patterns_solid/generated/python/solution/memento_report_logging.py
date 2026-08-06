"""DesignPatternsSolid | kind=design_pattern | label=memento | domain=report | tier=logging"""
from __future__ import annotations

from dataclasses import dataclass

@dataclass(frozen=True)
class ReportMemento:
    state: str

class ReportOriginator:
    def __init__(self) -> None:
        self.state = "report-init"

    def set_state(self, state: str) -> None:
        self.state = state

    def get_state(self) -> str:
        return self.state

    def save(self) -> ReportMemento:
        return ReportMemento(self.state)

    def restore(self, m: ReportMemento) -> None:
        self.state = m.state
