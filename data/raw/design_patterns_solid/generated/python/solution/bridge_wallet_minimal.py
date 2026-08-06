"""DesignPatternsSolid | kind=design_pattern | label=bridge | domain=wallet | tier=minimal"""
from __future__ import annotations

from abc import ABC, abstractmethod

class WalletImpl(ABC):
    @abstractmethod
    def write(self, msg: str) -> str: ...

class WalletFileImpl(WalletImpl):
    def write(self, msg: str) -> str:
        return f"file:wallet:{msg}"

class WalletMemoryImpl(WalletImpl):
    def write(self, msg: str) -> str:
        return f"mem:wallet:{msg}"

class WalletBridge(ABC):
    def __init__(self, impl: WalletImpl) -> None:
        self.impl = impl

    @abstractmethod
    def send(self, msg: str) -> str: ...

class WalletAlertBridge(WalletBridge):
    def send(self, msg: str) -> str:
        return self.impl.write("ALERT-" + msg)
