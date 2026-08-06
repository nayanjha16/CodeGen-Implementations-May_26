"""DesignPatternsSolid | kind=design_pattern | label=proxy | domain=search | tier=logging"""
from __future__ import annotations

from abc import ABC, abstractmethod

class SearchService(ABC):
    @abstractmethod
    def load(self, id: str) -> str: ...

class SearchRealService(SearchService):
    def load(self, id: str) -> str:
        return f"real-search:{id}"

class SearchProxy(SearchService):
    def __init__(self, allowed: bool) -> None:
        self.allowed = allowed
        self._real: SearchRealService | None = None

    def load(self, id: str) -> str:
        if not self.allowed:
            return "denied"
        if self._real is None:
            self._real = SearchRealService()
        return self._real.load(id)
