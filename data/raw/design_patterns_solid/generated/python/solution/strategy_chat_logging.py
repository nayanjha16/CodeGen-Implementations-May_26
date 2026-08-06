"""DesignPatternsSolid | kind=design_pattern | label=strategy | domain=chat | tier=logging"""
from __future__ import annotations

from abc import ABC, abstractmethod

class ChatStrategy(ABC):
    @abstractmethod
    def apply(self, amount: int) -> int: ...

class ChatNormalStrategy(ChatStrategy):
    def apply(self, amount: int) -> int:
        return amount

class ChatDiscountStrategy(ChatStrategy):
    def apply(self, amount: int) -> int:
        return amount // 2

class ChatContext:
    def __init__(self, strategy: ChatStrategy) -> None:
        self.strategy = strategy

    def set_strategy(self, strategy: ChatStrategy) -> None:
        self.strategy = strategy

    def execute(self, amount: int) -> int:
        return self.strategy.apply(amount)

    def tag(self) -> str:
        return "chat-strategy"
