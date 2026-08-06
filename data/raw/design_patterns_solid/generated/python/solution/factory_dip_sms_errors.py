"""DesignPatternsSolid | kind=combo | label=factory+dip | domain=sms | tier=errors"""
from __future__ import annotations

from abc import ABC, abstractmethod

class SmsProduct(ABC):
    @abstractmethod
    def operate(self) -> str:
        ...

class SmsBasicProduct(SmsProduct):
    def operate(self) -> str:
        return "basic-sms"

class SmsPremiumProduct(SmsProduct):
    def operate(self) -> str:
        return "premium-sms"

class SmsFactory:
    def create(self, type_name: str) -> SmsProduct:
        if not type_name:
            raise ValueError("type required")
        print(f"[log] create {type_name}")
        if type_name.lower() == "premium":
            return SmsPremiumProduct()
        return SmsBasicProduct()
