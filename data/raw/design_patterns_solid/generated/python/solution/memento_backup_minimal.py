"""DesignPatternsSolid | kind=design_pattern | label=memento | domain=backup | tier=minimal"""
from __future__ import annotations

from dataclasses import dataclass

@dataclass(frozen=True)
class BackupMemento:
    state: str

class BackupOriginator:
    def __init__(self) -> None:
        self.state = "backup-init"

    def set_state(self, state: str) -> None:
        self.state = state

    def get_state(self) -> str:
        return self.state

    def save(self) -> BackupMemento:
        return BackupMemento(self.state)

    def restore(self, m: BackupMemento) -> None:
        self.state = m.state
