"""DesignPatternsSolid | kind=design_pattern | label=bridge | domain=scheduling | tier=errors"""
from __future__ import annotations

from abc import ABC, abstractmethod

class SchedulingImpl(ABC):
    @abstractmethod
    def write(self, msg: str) -> str: ...

class SchedulingFileImpl(SchedulingImpl):
    def write(self, msg: str) -> str:
        return f"file:scheduling:{msg}"

class SchedulingMemoryImpl(SchedulingImpl):
    def write(self, msg: str) -> str:
        return f"mem:scheduling:{msg}"

class SchedulingBridge(ABC):
    def __init__(self, impl: SchedulingImpl) -> None:
        self.impl = impl

    @abstractmethod
    def send(self, msg: str) -> str: ...

class SchedulingAlertBridge(SchedulingBridge):
    def send(self, msg: str) -> str:
        return self.impl.write("ALERT-" + msg)
