"""DesignPatternsSolid | kind=solid | label=ocp | domain=chat | tier=errors"""
from __future__ import annotations

from abc import ABC, abstractmethod

class ChatDiscount(ABC):
    @abstractmethod
    def apply(self, price: int) -> int: ...

class ChatNoDiscount(ChatDiscount):
    def apply(self, price: int) -> int:
        return price

class ChatTenPercent(ChatDiscount):
    def apply(self, price: int) -> int:
        return price - price // 10

class ChatPriceEngine:
    def __init__(self, discount: ChatDiscount) -> None:
        self.discount = discount

    def quote(self, price: int) -> int:
        return self.discount.apply(price)

    def domain(self) -> str:
        return "chat"
