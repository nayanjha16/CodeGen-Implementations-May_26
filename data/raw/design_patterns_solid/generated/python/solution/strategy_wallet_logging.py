"""DesignPatternsSolid | kind=design_pattern | label=strategy | domain=wallet | tier=logging"""
from __future__ import annotations

from abc import ABC, abstractmethod

class WalletStrategy(ABC):
    @abstractmethod
    def apply(self, amount: int) -> int: ...

class WalletNormalStrategy(WalletStrategy):
    def apply(self, amount: int) -> int:
        return amount

class WalletDiscountStrategy(WalletStrategy):
    def apply(self, amount: int) -> int:
        return amount // 2

class WalletContext:
    def __init__(self, strategy: WalletStrategy) -> None:
        self.strategy = strategy

    def set_strategy(self, strategy: WalletStrategy) -> None:
        self.strategy = strategy

    def execute(self, amount: int) -> int:
        return self.strategy.apply(amount)

    def tag(self) -> str:
        return "wallet-strategy"
