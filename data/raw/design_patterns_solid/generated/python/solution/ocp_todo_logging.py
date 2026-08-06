"""DesignPatternsSolid | kind=solid | label=ocp | domain=todo | tier=logging"""
from __future__ import annotations

from abc import ABC, abstractmethod

class TodoDiscount(ABC):
    @abstractmethod
    def apply(self, price: int) -> int: ...

class TodoNoDiscount(TodoDiscount):
    def apply(self, price: int) -> int:
        return price

class TodoTenPercent(TodoDiscount):
    def apply(self, price: int) -> int:
        return price - price // 10

class TodoPriceEngine:
    def __init__(self, discount: TodoDiscount) -> None:
        self.discount = discount

    def quote(self, price: int) -> int:
        return self.discount.apply(price)

    def domain(self) -> str:
        return "todo"
