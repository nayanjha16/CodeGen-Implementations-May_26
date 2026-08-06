"""DesignPatternsSolid | kind=design_pattern | label=bridge | domain=shipping | tier=errors"""
from __future__ import annotations

from abc import ABC, abstractmethod

class ShippingImpl(ABC):
    @abstractmethod
    def write(self, msg: str) -> str: ...

class ShippingFileImpl(ShippingImpl):
    def write(self, msg: str) -> str:
        return f"file:shipping:{msg}"

class ShippingMemoryImpl(ShippingImpl):
    def write(self, msg: str) -> str:
        return f"mem:shipping:{msg}"

class ShippingBridge(ABC):
    def __init__(self, impl: ShippingImpl) -> None:
        self.impl = impl

    @abstractmethod
    def send(self, msg: str) -> str: ...

class ShippingAlertBridge(ShippingBridge):
    def send(self, msg: str) -> str:
        return self.impl.write("ALERT-" + msg)
