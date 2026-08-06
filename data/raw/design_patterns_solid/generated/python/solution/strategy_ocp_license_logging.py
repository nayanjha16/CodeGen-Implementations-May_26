"""DesignPatternsSolid | kind=combo | label=strategy+ocp | domain=license | tier=logging"""
from __future__ import annotations

from abc import ABC, abstractmethod

class LicenseStrategy(ABC):
    @abstractmethod
    def apply(self, amount: int) -> int: ...

class LicenseNormalStrategy(LicenseStrategy):
    def apply(self, amount: int) -> int:
        return amount

class LicenseDiscountStrategy(LicenseStrategy):
    def apply(self, amount: int) -> int:
        return amount // 2

class LicenseContext:
    def __init__(self, strategy: LicenseStrategy) -> None:
        self.strategy = strategy

    def set_strategy(self, strategy: LicenseStrategy) -> None:
        self.strategy = strategy

    def execute(self, amount: int) -> int:
        return self.strategy.apply(amount)

    def tag(self) -> str:
        return "license-strategy"
