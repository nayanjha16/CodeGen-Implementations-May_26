"""DesignPatternsSolid | kind=design_pattern | label=proxy | domain=game | tier=logging"""
from __future__ import annotations

from abc import ABC, abstractmethod

class GameService(ABC):
    @abstractmethod
    def load(self, id: str) -> str: ...

class GameRealService(GameService):
    def load(self, id: str) -> str:
        return f"real-game:{id}"

class GameProxy(GameService):
    def __init__(self, allowed: bool) -> None:
        self.allowed = allowed
        self._real: GameRealService | None = None

    def load(self, id: str) -> str:
        if not self.allowed:
            return "denied"
        if self._real is None:
            self._real = GameRealService()
        return self._real.load(id)
