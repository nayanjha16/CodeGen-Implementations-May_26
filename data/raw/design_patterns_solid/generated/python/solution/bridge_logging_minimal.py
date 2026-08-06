"""DesignPatternsSolid | kind=design_pattern | label=bridge | domain=logging | tier=minimal"""
from __future__ import annotations

from abc import ABC, abstractmethod

class LoggingImpl(ABC):
    @abstractmethod
    def write(self, msg: str) -> str: ...

class LoggingFileImpl(LoggingImpl):
    def write(self, msg: str) -> str:
        return f"file:logging:{msg}"

class LoggingMemoryImpl(LoggingImpl):
    def write(self, msg: str) -> str:
        return f"mem:logging:{msg}"

class LoggingBridge(ABC):
    def __init__(self, impl: LoggingImpl) -> None:
        self.impl = impl

    @abstractmethod
    def send(self, msg: str) -> str: ...

class LoggingAlertBridge(LoggingBridge):
    def send(self, msg: str) -> str:
        return self.impl.write("ALERT-" + msg)
