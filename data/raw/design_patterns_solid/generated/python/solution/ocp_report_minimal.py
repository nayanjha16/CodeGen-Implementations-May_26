"""DesignPatternsSolid | kind=solid | label=ocp | domain=report | tier=minimal"""
from __future__ import annotations

from abc import ABC, abstractmethod

class ReportDiscount(ABC):
    @abstractmethod
    def apply(self, price: int) -> int: ...

class ReportNoDiscount(ReportDiscount):
    def apply(self, price: int) -> int:
        return price

class ReportTenPercent(ReportDiscount):
    def apply(self, price: int) -> int:
        return price - price // 10

class ReportPriceEngine:
    def __init__(self, discount: ReportDiscount) -> None:
        self.discount = discount

    def quote(self, price: int) -> int:
        return self.discount.apply(price)

    def domain(self) -> str:
        return "report"
