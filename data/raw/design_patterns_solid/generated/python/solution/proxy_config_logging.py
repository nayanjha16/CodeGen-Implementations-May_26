"""DesignPatternsSolid | kind=design_pattern | label=proxy | domain=config | tier=logging"""
from __future__ import annotations

from abc import ABC, abstractmethod

class ConfigService(ABC):
    @abstractmethod
    def load(self, id: str) -> str: ...

class ConfigRealService(ConfigService):
    def load(self, id: str) -> str:
        return f"real-config:{id}"

class ConfigProxy(ConfigService):
    def __init__(self, allowed: bool) -> None:
        self.allowed = allowed
        self._real: ConfigRealService | None = None

    def load(self, id: str) -> str:
        if not self.allowed:
            return "denied"
        if self._real is None:
            self._real = ConfigRealService()
        return self._real.load(id)
