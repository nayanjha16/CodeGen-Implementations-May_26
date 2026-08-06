"""DesignPatternsSolid | kind=solid | label=ocp | domain=notifications | tier=logging"""
from __future__ import annotations

from abc import ABC, abstractmethod

class NotificationsDiscount(ABC):
    @abstractmethod
    def apply(self, price: int) -> int: ...

class NotificationsNoDiscount(NotificationsDiscount):
    def apply(self, price: int) -> int:
        return price

class NotificationsTenPercent(NotificationsDiscount):
    def apply(self, price: int) -> int:
        return price - price // 10

class NotificationsPriceEngine:
    def __init__(self, discount: NotificationsDiscount) -> None:
        self.discount = discount

    def quote(self, price: int) -> int:
        return self.discount.apply(price)

    def domain(self) -> str:
        return "notifications"
