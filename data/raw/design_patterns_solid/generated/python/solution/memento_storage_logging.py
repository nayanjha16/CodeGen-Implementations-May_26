"""DesignPatternsSolid | kind=design_pattern | label=memento | domain=storage | tier=logging"""
from __future__ import annotations

from dataclasses import dataclass

@dataclass(frozen=True)
class StorageMemento:
    state: str

class StorageOriginator:
    def __init__(self) -> None:
        self.state = "storage-init"

    def set_state(self, state: str) -> None:
        self.state = state

    def get_state(self) -> str:
        return self.state

    def save(self) -> StorageMemento:
        return StorageMemento(self.state)

    def restore(self, m: StorageMemento) -> None:
        self.state = m.state
