"""DesignPatternsSolid | kind=design_pattern | label=memento | domain=streaming | tier=errors"""
from __future__ import annotations

from dataclasses import dataclass

@dataclass(frozen=True)
class StreamingMemento:
    state: str

class StreamingOriginator:
    def __init__(self) -> None:
        self.state = "streaming-init"

    def set_state(self, state: str) -> None:
        self.state = state

    def get_state(self) -> str:
        return self.state

    def save(self) -> StreamingMemento:
        return StreamingMemento(self.state)

    def restore(self, m: StreamingMemento) -> None:
        self.state = m.state
