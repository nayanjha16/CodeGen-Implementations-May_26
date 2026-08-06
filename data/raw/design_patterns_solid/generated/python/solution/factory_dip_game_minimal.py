"""DesignPatternsSolid | kind=combo | label=factory+dip | domain=game | tier=minimal"""
from __future__ import annotations

from abc import ABC, abstractmethod

class GameProduct(ABC):
    @abstractmethod
    def operate(self) -> str:
        ...

class GameBasicProduct(GameProduct):
    def operate(self) -> str:
        return "basic-game"

class GamePremiumProduct(GameProduct):
    def operate(self) -> str:
        return "premium-game"

class GameFactory:
    def create(self, type_name: str) -> GameProduct:
        if type_name.lower() == "premium":
            return GamePremiumProduct()
        return GameBasicProduct()
