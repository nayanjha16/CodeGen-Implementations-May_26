"""DesignPatternsSolid | kind=design_pattern | label=bridge | domain=audio | tier=minimal"""
from __future__ import annotations

from abc import ABC, abstractmethod

class AudioImpl(ABC):
    @abstractmethod
    def write(self, msg: str) -> str: ...

class AudioFileImpl(AudioImpl):
    def write(self, msg: str) -> str:
        return f"file:audio:{msg}"

class AudioMemoryImpl(AudioImpl):
    def write(self, msg: str) -> str:
        return f"mem:audio:{msg}"

class AudioBridge(ABC):
    def __init__(self, impl: AudioImpl) -> None:
        self.impl = impl

    @abstractmethod
    def send(self, msg: str) -> str: ...

class AudioAlertBridge(AudioBridge):
    def send(self, msg: str) -> str:
        return self.impl.write("ALERT-" + msg)
