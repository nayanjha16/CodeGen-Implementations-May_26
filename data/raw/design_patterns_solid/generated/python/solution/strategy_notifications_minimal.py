"""DesignPatternsSolid | kind=design_pattern | label=strategy | domain=notifications | tier=minimal"""
from __future__ import annotations

from abc import ABC, abstractmethod

class NotificationsStrategy(ABC):
    @abstractmethod
    def apply(self, amount: int) -> int: ...

class NotificationsNormalStrategy(NotificationsStrategy):
    def apply(self, amount: int) -> int:
        return amount

class NotificationsDiscountStrategy(NotificationsStrategy):
    def apply(self, amount: int) -> int:
        return amount // 2

class NotificationsContext:
    def __init__(self, strategy: NotificationsStrategy) -> None:
        self.strategy = strategy

    def set_strategy(self, strategy: NotificationsStrategy) -> None:
        self.strategy = strategy

    def execute(self, amount: int) -> int:
        return self.strategy.apply(amount)

    def tag(self) -> str:
        return "notifications-strategy"
