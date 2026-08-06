"""DesignPatternsSolid | kind=design_pattern | label=memento | domain=video | tier=minimal"""
from __future__ import annotations

from dataclasses import dataclass

@dataclass(frozen=True)
class VideoMemento:
    state: str

class VideoOriginator:
    def __init__(self) -> None:
        self.state = "video-init"

    def set_state(self, state: str) -> None:
        self.state = state

    def get_state(self) -> str:
        return self.state

    def save(self) -> VideoMemento:
        return VideoMemento(self.state)

    def restore(self, m: VideoMemento) -> None:
        self.state = m.state
