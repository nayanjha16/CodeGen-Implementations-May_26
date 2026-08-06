"""DesignPatternsSolid | kind=design_pattern | label=bridge | domain=video | tier=logging"""
from __future__ import annotations

from abc import ABC, abstractmethod

class VideoImpl(ABC):
    @abstractmethod
    def write(self, msg: str) -> str: ...

class VideoFileImpl(VideoImpl):
    def write(self, msg: str) -> str:
        return f"file:video:{msg}"

class VideoMemoryImpl(VideoImpl):
    def write(self, msg: str) -> str:
        return f"mem:video:{msg}"

class VideoBridge(ABC):
    def __init__(self, impl: VideoImpl) -> None:
        self.impl = impl

    @abstractmethod
    def send(self, msg: str) -> str: ...

class VideoAlertBridge(VideoBridge):
    def send(self, msg: str) -> str:
        return self.impl.write("ALERT-" + msg)
