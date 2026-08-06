"""DesignPatternsSolid | kind=design_pattern | label=bridge | domain=tax | tier=minimal"""
from __future__ import annotations

from abc import ABC, abstractmethod

class TaxImpl(ABC):
    @abstractmethod
    def write(self, msg: str) -> str: ...

class TaxFileImpl(TaxImpl):
    def write(self, msg: str) -> str:
        return f"file:tax:{msg}"

class TaxMemoryImpl(TaxImpl):
    def write(self, msg: str) -> str:
        return f"mem:tax:{msg}"

class TaxBridge(ABC):
    def __init__(self, impl: TaxImpl) -> None:
        self.impl = impl

    @abstractmethod
    def send(self, msg: str) -> str: ...

class TaxAlertBridge(TaxBridge):
    def send(self, msg: str) -> str:
        return self.impl.write("ALERT-" + msg)
