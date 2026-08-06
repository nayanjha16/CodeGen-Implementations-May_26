"""DesignPatternsSolid | kind=solid | label=ocp | domain=audio | tier=minimal"""
from __future__ import annotations

from abc import ABC, abstractmethod

class AudioDiscount(ABC):
    @abstractmethod
    def apply(self, price: int) -> int: ...

class AudioNoDiscount(AudioDiscount):
    def apply(self, price: int) -> int:
        return price

class AudioTenPercent(AudioDiscount):
    def apply(self, price: int) -> int:
        return price - price // 10

class AudioPriceEngine:
    def __init__(self, discount: AudioDiscount) -> None:
        self.discount = discount

    def quote(self, price: int) -> int:
        return self.discount.apply(price)

    def domain(self) -> str:
        return "audio"
