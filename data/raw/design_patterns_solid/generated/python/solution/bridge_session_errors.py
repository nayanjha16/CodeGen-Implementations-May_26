"""DesignPatternsSolid | kind=design_pattern | label=bridge | domain=session | tier=errors"""
from __future__ import annotations

from abc import ABC, abstractmethod

class SessionImpl(ABC):
    @abstractmethod
    def write(self, msg: str) -> str: ...

class SessionFileImpl(SessionImpl):
    def write(self, msg: str) -> str:
        return f"file:session:{msg}"

class SessionMemoryImpl(SessionImpl):
    def write(self, msg: str) -> str:
        return f"mem:session:{msg}"

class SessionBridge(ABC):
    def __init__(self, impl: SessionImpl) -> None:
        self.impl = impl

    @abstractmethod
    def send(self, msg: str) -> str: ...

class SessionAlertBridge(SessionBridge):
    def send(self, msg: str) -> str:
        return self.impl.write("ALERT-" + msg)
