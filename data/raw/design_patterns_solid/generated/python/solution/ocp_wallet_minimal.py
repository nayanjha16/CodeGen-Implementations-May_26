"""DesignPatternsSolid | kind=solid | label=ocp | domain=wallet | tier=minimal"""
from __future__ import annotations

from abc import ABC, abstractmethod

class WalletDiscount(ABC):
    @abstractmethod
    def apply(self, price: int) -> int: ...

class WalletNoDiscount(WalletDiscount):
    def apply(self, price: int) -> int:
        return price

class WalletTenPercent(WalletDiscount):
    def apply(self, price: int) -> int:
        return price - price // 10

class WalletPriceEngine:
    def __init__(self, discount: WalletDiscount) -> None:
        self.discount = discount

    def quote(self, price: int) -> int:
        return self.discount.apply(price)

    def domain(self) -> str:
        return "wallet"
