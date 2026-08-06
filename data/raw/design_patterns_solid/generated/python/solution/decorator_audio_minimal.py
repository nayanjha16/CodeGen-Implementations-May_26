"""DesignPatternsSolid | kind=design_pattern | label=decorator | domain=audio | tier=minimal"""
from __future__ import annotations

from abc import ABC, abstractmethod

class AudioComponent(ABC):
    @abstractmethod
    def process(self, input: str) -> str: ...

class AudioCore(AudioComponent):
    def process(self, input: str) -> str:
        return f"audio:{input}"

class AudioUpperDecorator(AudioComponent):
    def __init__(self, inner: AudioComponent) -> None:
        self.inner = inner

    def process(self, input: str) -> str:
        return self.inner.process(input).upper()
