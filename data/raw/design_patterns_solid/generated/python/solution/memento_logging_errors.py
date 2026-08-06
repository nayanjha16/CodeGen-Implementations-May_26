"""DesignPatternsSolid | kind=design_pattern | label=memento | domain=logging | tier=errors"""
from __future__ import annotations

from dataclasses import dataclass

@dataclass(frozen=True)
class LoggingMemento:
    state: str

class LoggingOriginator:
    def __init__(self) -> None:
        self.state = "logging-init"

    def set_state(self, state: str) -> None:
        self.state = state

    def get_state(self) -> str:
        return self.state

    def save(self) -> LoggingMemento:
        return LoggingMemento(self.state)

    def restore(self, m: LoggingMemento) -> None:
        self.state = m.state
