"""DesignPatternsSolid | kind=design_pattern | label=proxy | domain=license | tier=logging"""
from __future__ import annotations

from abc import ABC, abstractmethod

class LicenseService(ABC):
    @abstractmethod
    def load(self, id: str) -> str: ...

class LicenseRealService(LicenseService):
    def load(self, id: str) -> str:
        return f"real-license:{id}"

class LicenseProxy(LicenseService):
    def __init__(self, allowed: bool) -> None:
        self.allowed = allowed
        self._real: LicenseRealService | None = None

    def load(self, id: str) -> str:
        if not self.allowed:
            return "denied"
        if self._real is None:
            self._real = LicenseRealService()
        return self._real.load(id)
