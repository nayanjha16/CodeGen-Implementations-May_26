"""DesignPatternsSolid | kind=design_pattern | label=strategy | domain=profile | tier=logging"""
from __future__ import annotations

from abc import ABC, abstractmethod

class ProfileStrategy(ABC):
    @abstractmethod
    def apply(self, amount: int) -> int: ...

class ProfileNormalStrategy(ProfileStrategy):
    def apply(self, amount: int) -> int:
        return amount

class ProfileDiscountStrategy(ProfileStrategy):
    def apply(self, amount: int) -> int:
        return amount // 2

class ProfileContext:
    def __init__(self, strategy: ProfileStrategy) -> None:
        self.strategy = strategy

    def set_strategy(self, strategy: ProfileStrategy) -> None:
        self.strategy = strategy

    def execute(self, amount: int) -> int:
        return self.strategy.apply(amount)

    def tag(self) -> str:
        return "profile-strategy"
