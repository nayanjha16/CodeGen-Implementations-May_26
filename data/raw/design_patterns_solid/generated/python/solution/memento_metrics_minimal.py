"""DesignPatternsSolid | kind=design_pattern | label=memento | domain=metrics | tier=minimal"""
from __future__ import annotations

from dataclasses import dataclass

@dataclass(frozen=True)
class MetricsMemento:
    state: str

class MetricsOriginator:
    def __init__(self) -> None:
        self.state = "metrics-init"

    def set_state(self, state: str) -> None:
        self.state = state

    def get_state(self) -> str:
        return self.state

    def save(self) -> MetricsMemento:
        return MetricsMemento(self.state)

    def restore(self, m: MetricsMemento) -> None:
        self.state = m.state
