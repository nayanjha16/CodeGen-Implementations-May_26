"""DesignPatternsSolid | kind=solid | label=ocp | domain=editor | tier=errors"""
from __future__ import annotations

from abc import ABC, abstractmethod

class EditorDiscount(ABC):
    @abstractmethod
    def apply(self, price: int) -> int: ...

class EditorNoDiscount(EditorDiscount):
    def apply(self, price: int) -> int:
        return price

class EditorTenPercent(EditorDiscount):
    def apply(self, price: int) -> int:
        return price - price // 10

class EditorPriceEngine:
    def __init__(self, discount: EditorDiscount) -> None:
        self.discount = discount

    def quote(self, price: int) -> int:
        return self.discount.apply(price)

    def domain(self) -> str:
        return "editor"
