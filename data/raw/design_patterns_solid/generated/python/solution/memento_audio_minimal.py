"""DesignPatternsSolid | kind=design_pattern | label=memento | domain=audio | tier=minimal"""
from __future__ import annotations

from dataclasses import dataclass

@dataclass(frozen=True)
class AudioMemento:
    state: str

class AudioOriginator:
    def __init__(self) -> None:
        self.state = "audio-init"

    def set_state(self, state: str) -> None:
        self.state = state

    def get_state(self) -> str:
        return self.state

    def save(self) -> AudioMemento:
        return AudioMemento(self.state)

    def restore(self, m: AudioMemento) -> None:
        self.state = m.state
