"""DesignPatternsSolid | kind=design_pattern | label=strategy | domain=sync | tier=minimal"""
from __future__ import annotations

from abc import ABC, abstractmethod

class SyncStrategy(ABC):
    @abstractmethod
    def apply(self, amount: int) -> int: ...

class SyncNormalStrategy(SyncStrategy):
    def apply(self, amount: int) -> int:
        return amount

class SyncDiscountStrategy(SyncStrategy):
    def apply(self, amount: int) -> int:
        return amount // 2

class SyncContext:
    def __init__(self, strategy: SyncStrategy) -> None:
        self.strategy = strategy

    def set_strategy(self, strategy: SyncStrategy) -> None:
        self.strategy = strategy

    def execute(self, amount: int) -> int:
        return self.strategy.apply(amount)

    def tag(self) -> str:
        return "sync-strategy"
