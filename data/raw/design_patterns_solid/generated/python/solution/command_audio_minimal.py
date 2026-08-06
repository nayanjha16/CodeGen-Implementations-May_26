"""DesignPatternsSolid | kind=design_pattern | label=command | domain=audio | tier=minimal"""
from __future__ import annotations

from abc import ABC, abstractmethod

class AudioCommand(ABC):
    @abstractmethod
    def execute(self) -> str: ...

class AudioReceiver:
    def action(self, x: str) -> str:
        return f"done-audio:{x}"

class AudioActionCommand(AudioCommand):
    def __init__(self, receiver: AudioReceiver, payload: str) -> None:
        self.receiver = receiver
        self.payload = payload

    def execute(self) -> str:
        return self.receiver.action(self.payload)
