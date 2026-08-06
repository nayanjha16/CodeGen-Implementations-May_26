"""DesignPatternsSolid | kind=design_pattern | label=memento | domain=license | tier=minimal"""
from __future__ import annotations

from dataclasses import dataclass

@dataclass(frozen=True)
class LicenseMemento:
    state: str

class LicenseOriginator:
    def __init__(self) -> None:
        self.state = "license-init"

    def set_state(self, state: str) -> None:
        self.state = state

    def get_state(self) -> str:
        return self.state

    def save(self) -> LicenseMemento:
        return LicenseMemento(self.state)

    def restore(self, m: LicenseMemento) -> None:
        self.state = m.state
