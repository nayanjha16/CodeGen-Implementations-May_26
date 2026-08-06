"""DesignPatternsSolid | kind=design_pattern | label=bridge | domain=editor | tier=minimal"""
from __future__ import annotations

from abc import ABC, abstractmethod

class EditorImpl(ABC):
    @abstractmethod
    def write(self, msg: str) -> str: ...

class EditorFileImpl(EditorImpl):
    def write(self, msg: str) -> str:
        return f"file:editor:{msg}"

class EditorMemoryImpl(EditorImpl):
    def write(self, msg: str) -> str:
        return f"mem:editor:{msg}"

class EditorBridge(ABC):
    def __init__(self, impl: EditorImpl) -> None:
        self.impl = impl

    @abstractmethod
    def send(self, msg: str) -> str: ...

class EditorAlertBridge(EditorBridge):
    def send(self, msg: str) -> str:
        return self.impl.write("ALERT-" + msg)
