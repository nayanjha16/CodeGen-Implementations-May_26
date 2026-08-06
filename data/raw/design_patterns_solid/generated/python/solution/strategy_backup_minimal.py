"""DesignPatternsSolid | kind=design_pattern | label=strategy | domain=backup | tier=minimal"""
from __future__ import annotations

from abc import ABC, abstractmethod

class BackupStrategy(ABC):
    @abstractmethod
    def apply(self, amount: int) -> int: ...

class BackupNormalStrategy(BackupStrategy):
    def apply(self, amount: int) -> int:
        return amount

class BackupDiscountStrategy(BackupStrategy):
    def apply(self, amount: int) -> int:
        return amount // 2

class BackupContext:
    def __init__(self, strategy: BackupStrategy) -> None:
        self.strategy = strategy

    def set_strategy(self, strategy: BackupStrategy) -> None:
        self.strategy = strategy

    def execute(self, amount: int) -> int:
        return self.strategy.apply(amount)

    def tag(self) -> str:
        return "backup-strategy"
