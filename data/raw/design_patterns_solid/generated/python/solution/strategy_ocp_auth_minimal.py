"""DesignPatternsSolid | kind=combo | label=strategy+ocp | domain=auth | tier=minimal"""
from __future__ import annotations

from abc import ABC, abstractmethod

class AuthStrategy(ABC):
    @abstractmethod
    def apply(self, amount: int) -> int: ...

class AuthNormalStrategy(AuthStrategy):
    def apply(self, amount: int) -> int:
        return amount

class AuthDiscountStrategy(AuthStrategy):
    def apply(self, amount: int) -> int:
        return amount // 2

class AuthContext:
    def __init__(self, strategy: AuthStrategy) -> None:
        self.strategy = strategy

    def set_strategy(self, strategy: AuthStrategy) -> None:
        self.strategy = strategy

    def execute(self, amount: int) -> int:
        return self.strategy.apply(amount)

    def tag(self) -> str:
        return "auth-strategy"
