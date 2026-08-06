"""DesignPatternsSolid | kind=design_pattern | label=memento | domain=cache | tier=minimal"""
from __future__ import annotations

from dataclasses import dataclass

@dataclass(frozen=True)
class CacheMemento:
    state: str

class CacheOriginator:
    def __init__(self) -> None:
        self.state = "cache-init"

    def set_state(self, state: str) -> None:
        self.state = state

    def get_state(self) -> str:
        return self.state

    def save(self) -> CacheMemento:
        return CacheMemento(self.state)

    def restore(self, m: CacheMemento) -> None:
        self.state = m.state
