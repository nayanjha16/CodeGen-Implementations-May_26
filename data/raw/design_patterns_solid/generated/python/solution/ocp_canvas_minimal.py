"""DesignPatternsSolid | kind=solid | label=ocp | domain=canvas | tier=minimal"""
from __future__ import annotations

from abc import ABC, abstractmethod

class CanvasDiscount(ABC):
    @abstractmethod
    def apply(self, price: int) -> int: ...

class CanvasNoDiscount(CanvasDiscount):
    def apply(self, price: int) -> int:
        return price

class CanvasTenPercent(CanvasDiscount):
    def apply(self, price: int) -> int:
        return price - price // 10

class CanvasPriceEngine:
    def __init__(self, discount: CanvasDiscount) -> None:
        self.discount = discount

    def quote(self, price: int) -> int:
        return self.discount.apply(price)

    def domain(self) -> str:
        return "canvas"
