"""DesignPatternsSolid | kind=design_pattern | label=bridge | domain=sync | tier=minimal"""
from __future__ import annotations

from abc import ABC, abstractmethod

class SyncImpl(ABC):
    @abstractmethod
    def write(self, msg: str) -> str: ...

class SyncFileImpl(SyncImpl):
    def write(self, msg: str) -> str:
        return f"file:sync:{msg}"

class SyncMemoryImpl(SyncImpl):
    def write(self, msg: str) -> str:
        return f"mem:sync:{msg}"

class SyncBridge(ABC):
    def __init__(self, impl: SyncImpl) -> None:
        self.impl = impl

    @abstractmethod
    def send(self, msg: str) -> str: ...

class SyncAlertBridge(SyncBridge):
    def send(self, msg: str) -> str:
        return self.impl.write("ALERT-" + msg)
