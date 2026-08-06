"""DesignPatternsSolid | kind=design_pattern | label=factory | domain=payments | tier=minimal"""
from __future__ import annotations

from abc import ABC, abstractmethod

class PaymentsProduct(ABC):
    @abstractmethod
    def operate(self) -> str:
        ...

class PaymentsBasicProduct(PaymentsProduct):
    def operate(self) -> str:
        return "basic-payments"

class PaymentsPremiumProduct(PaymentsProduct):
    def operate(self) -> str:
        return "premium-payments"

class PaymentsFactory:
    def create(self, type_name: str) -> PaymentsProduct:
        if type_name.lower() == "premium":
            return PaymentsPremiumProduct()
        return PaymentsBasicProduct()
