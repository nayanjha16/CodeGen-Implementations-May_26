"""DesignPatternsSolid | kind=design_pattern | label=bridge | domain=canvas | tier=logging"""
from __future__ import annotations

from abc import ABC, abstractmethod

class CanvasImpl(ABC):
    @abstractmethod
    def write(self, msg: str) -> str: ...

class CanvasFileImpl(CanvasImpl):
    def write(self, msg: str) -> str:
        return f"file:canvas:{msg}"

class CanvasMemoryImpl(CanvasImpl):
    def write(self, msg: str) -> str:
        return f"mem:canvas:{msg}"

class CanvasBridge(ABC):
    def __init__(self, impl: CanvasImpl) -> None:
        self.impl = impl

    @abstractmethod
    def send(self, msg: str) -> str: ...

class CanvasAlertBridge(CanvasBridge):
    def send(self, msg: str) -> str:
        return self.impl.write("ALERT-" + msg)
