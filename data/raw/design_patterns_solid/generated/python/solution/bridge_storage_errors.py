"""DesignPatternsSolid | kind=design_pattern | label=bridge | domain=storage | tier=errors"""
from __future__ import annotations

from abc import ABC, abstractmethod

class StorageImpl(ABC):
    @abstractmethod
    def write(self, msg: str) -> str: ...

class StorageFileImpl(StorageImpl):
    def write(self, msg: str) -> str:
        return f"file:storage:{msg}"

class StorageMemoryImpl(StorageImpl):
    def write(self, msg: str) -> str:
        return f"mem:storage:{msg}"

class StorageBridge(ABC):
    def __init__(self, impl: StorageImpl) -> None:
        self.impl = impl

    @abstractmethod
    def send(self, msg: str) -> str: ...

class StorageAlertBridge(StorageBridge):
    def send(self, msg: str) -> str:
        return self.impl.write("ALERT-" + msg)
