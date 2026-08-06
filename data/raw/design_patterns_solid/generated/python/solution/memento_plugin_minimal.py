"""DesignPatternsSolid | kind=design_pattern | label=memento | domain=plugin | tier=minimal"""
from __future__ import annotations

from dataclasses import dataclass

@dataclass(frozen=True)
class PluginMemento:
    state: str

class PluginOriginator:
    def __init__(self) -> None:
        self.state = "plugin-init"

    def set_state(self, state: str) -> None:
        self.state = state

    def get_state(self) -> str:
        return self.state

    def save(self) -> PluginMemento:
        return PluginMemento(self.state)

    def restore(self, m: PluginMemento) -> None:
        self.state = m.state
