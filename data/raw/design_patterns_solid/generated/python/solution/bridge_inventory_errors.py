"""DesignPatternsSolid | kind=design_pattern | label=bridge | domain=inventory | tier=errors"""
from __future__ import annotations

from abc import ABC, abstractmethod

class InventoryImpl(ABC):
    @abstractmethod
    def write(self, msg: str) -> str: ...

class InventoryFileImpl(InventoryImpl):
    def write(self, msg: str) -> str:
        return f"file:inventory:{msg}"

class InventoryMemoryImpl(InventoryImpl):
    def write(self, msg: str) -> str:
        return f"mem:inventory:{msg}"

class InventoryBridge(ABC):
    def __init__(self, impl: InventoryImpl) -> None:
        self.impl = impl

    @abstractmethod
    def send(self, msg: str) -> str: ...

class InventoryAlertBridge(InventoryBridge):
    def send(self, msg: str) -> str:
        return self.impl.write("ALERT-" + msg)
