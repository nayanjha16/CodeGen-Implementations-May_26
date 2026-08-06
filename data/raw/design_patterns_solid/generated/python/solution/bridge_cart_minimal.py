"""DesignPatternsSolid | kind=design_pattern | label=bridge | domain=cart | tier=minimal"""
from __future__ import annotations

from abc import ABC, abstractmethod

class CartImpl(ABC):
    @abstractmethod
    def write(self, msg: str) -> str: ...

class CartFileImpl(CartImpl):
    def write(self, msg: str) -> str:
        return f"file:cart:{msg}"

class CartMemoryImpl(CartImpl):
    def write(self, msg: str) -> str:
        return f"mem:cart:{msg}"

class CartBridge(ABC):
    def __init__(self, impl: CartImpl) -> None:
        self.impl = impl

    @abstractmethod
    def send(self, msg: str) -> str: ...

class CartAlertBridge(CartBridge):
    def send(self, msg: str) -> str:
        return self.impl.write("ALERT-" + msg)
