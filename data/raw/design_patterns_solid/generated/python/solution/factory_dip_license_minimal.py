"""DesignPatternsSolid | kind=combo | label=factory+dip | domain=license | tier=minimal"""
from __future__ import annotations

from abc import ABC, abstractmethod

class LicenseProduct(ABC):
    @abstractmethod
    def operate(self) -> str:
        ...

class LicenseBasicProduct(LicenseProduct):
    def operate(self) -> str:
        return "basic-license"

class LicensePremiumProduct(LicenseProduct):
    def operate(self) -> str:
        return "premium-license"

class LicenseFactory:
    def create(self, type_name: str) -> LicenseProduct:
        if type_name.lower() == "premium":
            return LicensePremiumProduct()
        return LicenseBasicProduct()
