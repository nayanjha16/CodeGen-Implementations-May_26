"""DesignPatternsSolid | kind=design_pattern | label=bridge | domain=discount | tier=errors"""
from __future__ import annotations

from abc import ABC, abstractmethod

class DiscountImpl(ABC):
    @abstractmethod
    def write(self, msg: str) -> str: ...

class DiscountFileImpl(DiscountImpl):
    def write(self, msg: str) -> str:
        return f"file:discount:{msg}"

class DiscountMemoryImpl(DiscountImpl):
    def write(self, msg: str) -> str:
        return f"mem:discount:{msg}"

class DiscountBridge(ABC):
    def __init__(self, impl: DiscountImpl) -> None:
        self.impl = impl

    @abstractmethod
    def send(self, msg: str) -> str: ...

class DiscountAlertBridge(DiscountBridge):
    def send(self, msg: str) -> str:
        return self.impl.write("ALERT-" + msg)
