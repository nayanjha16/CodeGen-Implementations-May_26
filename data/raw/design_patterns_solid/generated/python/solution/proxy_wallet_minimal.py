"""DesignPatternsSolid | kind=design_pattern | label=proxy | domain=wallet | tier=minimal"""
from __future__ import annotations

from abc import ABC, abstractmethod

class WalletService(ABC):
    @abstractmethod
    def load(self, id: str) -> str: ...

class WalletRealService(WalletService):
    def load(self, id: str) -> str:
        return f"real-wallet:{id}"

class WalletProxy(WalletService):
    def __init__(self, allowed: bool) -> None:
        self.allowed = allowed
        self._real: WalletRealService | None = None

    def load(self, id: str) -> str:
        if not self.allowed:
            return "denied"
        if self._real is None:
            self._real = WalletRealService()
        return self._real.load(id)
