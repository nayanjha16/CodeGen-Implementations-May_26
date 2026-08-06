"""DesignPatternsSolid | kind=combo | label=strategy+ocp | domain=shipping | tier=minimal"""
from __future__ import annotations

from abc import ABC, abstractmethod

class ShippingStrategy(ABC):
    @abstractmethod
    def apply(self, amount: int) -> int: ...

class ShippingNormalStrategy(ShippingStrategy):
    def apply(self, amount: int) -> int:
        return amount

class ShippingDiscountStrategy(ShippingStrategy):
    def apply(self, amount: int) -> int:
        return amount // 2

class ShippingContext:
    def __init__(self, strategy: ShippingStrategy) -> None:
        self.strategy = strategy

    def set_strategy(self, strategy: ShippingStrategy) -> None:
        self.strategy = strategy

    def execute(self, amount: int) -> int:
        return self.strategy.apply(amount)

    def tag(self) -> str:
        return "shipping-strategy"
