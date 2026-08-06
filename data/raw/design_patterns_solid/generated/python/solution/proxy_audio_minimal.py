"""DesignPatternsSolid | kind=design_pattern | label=proxy | domain=audio | tier=minimal"""
from __future__ import annotations

from abc import ABC, abstractmethod

class AudioService(ABC):
    @abstractmethod
    def load(self, id: str) -> str: ...

class AudioRealService(AudioService):
    def load(self, id: str) -> str:
        return f"real-audio:{id}"

class AudioProxy(AudioService):
    def __init__(self, allowed: bool) -> None:
        self.allowed = allowed
        self._real: AudioRealService | None = None

    def load(self, id: str) -> str:
        if not self.allowed:
            return "denied"
        if self._real is None:
            self._real = AudioRealService()
        return self._real.load(id)
