"""DesignPatternsSolid | kind=combo | label=strategy+ocp | domain=report | tier=errors"""
from __future__ import annotations

from abc import ABC, abstractmethod

class ReportStrategy(ABC):
    @abstractmethod
    def apply(self, amount: int) -> int: ...

class ReportNormalStrategy(ReportStrategy):
    def apply(self, amount: int) -> int:
        return amount

class ReportDiscountStrategy(ReportStrategy):
    def apply(self, amount: int) -> int:
        return amount // 2

class ReportContext:
    def __init__(self, strategy: ReportStrategy) -> None:
        self.strategy = strategy

    def set_strategy(self, strategy: ReportStrategy) -> None:
        self.strategy = strategy

    def execute(self, amount: int) -> int:
        if amount < 0:
            raise ValueError("amount >= 0")
        return self.strategy.apply(amount)

    def tag(self) -> str:
        return "report-strategy"
