"""DesignPatternsSolid | kind=solid | label=ocp | domain=license | tier=logging"""
from __future__ import annotations

from abc import ABC, abstractmethod

class LicenseDiscount(ABC):
    @abstractmethod
    def apply(self, price: int) -> int: ...

class LicenseNoDiscount(LicenseDiscount):
    def apply(self, price: int) -> int:
        return price

class LicenseTenPercent(LicenseDiscount):
    def apply(self, price: int) -> int:
        return price - price // 10

class LicensePriceEngine:
    def __init__(self, discount: LicenseDiscount) -> None:
        self.discount = discount

    def quote(self, price: int) -> int:
        return self.discount.apply(price)

    def domain(self) -> str:
        return "license"
