"""DesignPatternsSolid | kind=design_pattern | label=factory | domain=notifications | tier=errors"""
from __future__ import annotations

from abc import ABC, abstractmethod

class NotificationsProduct(ABC):
    @abstractmethod
    def operate(self) -> str:
        ...

class NotificationsBasicProduct(NotificationsProduct):
    def operate(self) -> str:
        return "basic-notifications"

class NotificationsPremiumProduct(NotificationsProduct):
    def operate(self) -> str:
        return "premium-notifications"

class NotificationsFactory:
    def create(self, type_name: str) -> NotificationsProduct:
        if not type_name:
            raise ValueError("type required")
        print(f"[log] create {type_name}")
        if type_name.lower() == "premium":
            return NotificationsPremiumProduct()
        return NotificationsBasicProduct()
