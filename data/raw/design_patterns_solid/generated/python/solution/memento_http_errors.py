"""DesignPatternsSolid | kind=design_pattern | label=memento | domain=http | tier=errors"""
from __future__ import annotations

from dataclasses import dataclass

@dataclass(frozen=True)
class HttpMemento:
    state: str

class HttpOriginator:
    def __init__(self) -> None:
        self.state = "http-init"

    def set_state(self, state: str) -> None:
        self.state = state

    def get_state(self) -> str:
        return self.state

    def save(self) -> HttpMemento:
        return HttpMemento(self.state)

    def restore(self, m: HttpMemento) -> None:
        self.state = m.state
