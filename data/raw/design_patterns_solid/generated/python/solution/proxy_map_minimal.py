"""DesignPatternsSolid | kind=design_pattern | label=proxy | domain=map | tier=minimal"""
from __future__ import annotations

from abc import ABC, abstractmethod

class MapService(ABC):
    @abstractmethod
    def load(self, id: str) -> str: ...

class MapRealService(MapService):
    def load(self, id: str) -> str:
        return f"real-map:{id}"

class MapProxy(MapService):
    def __init__(self, allowed: bool) -> None:
        self.allowed = allowed
        self._real: MapRealService | None = None

    def load(self, id: str) -> str:
        if not self.allowed:
            return "denied"
        if self._real is None:
            self._real = MapRealService()
        return self._real.load(id)
