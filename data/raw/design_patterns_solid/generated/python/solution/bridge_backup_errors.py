"""DesignPatternsSolid | kind=design_pattern | label=bridge | domain=backup | tier=errors"""
from __future__ import annotations

from abc import ABC, abstractmethod

class BackupImpl(ABC):
    @abstractmethod
    def write(self, msg: str) -> str: ...

class BackupFileImpl(BackupImpl):
    def write(self, msg: str) -> str:
        return f"file:backup:{msg}"

class BackupMemoryImpl(BackupImpl):
    def write(self, msg: str) -> str:
        return f"mem:backup:{msg}"

class BackupBridge(ABC):
    def __init__(self, impl: BackupImpl) -> None:
        self.impl = impl

    @abstractmethod
    def send(self, msg: str) -> str: ...

class BackupAlertBridge(BackupBridge):
    def send(self, msg: str) -> str:
        return self.impl.write("ALERT-" + msg)
