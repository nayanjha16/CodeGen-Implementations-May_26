"""DesignPatternsSolid | kind=solid | label=ocp | domain=backup | tier=logging"""
from __future__ import annotations

from abc import ABC, abstractmethod

class BackupDiscount(ABC):
    @abstractmethod
    def apply(self, price: int) -> int: ...

class BackupNoDiscount(BackupDiscount):
    def apply(self, price: int) -> int:
        return price

class BackupTenPercent(BackupDiscount):
    def apply(self, price: int) -> int:
        return price - price // 10

class BackupPriceEngine:
    def __init__(self, discount: BackupDiscount) -> None:
        self.discount = discount

    def quote(self, price: int) -> int:
        return self.discount.apply(price)

    def domain(self) -> str:
        return "backup"
