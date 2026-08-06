"""DesignPatternsSolid | kind=combo | label=factory+dip | domain=report | tier=errors"""
from __future__ import annotations

from abc import ABC, abstractmethod

class ReportProduct(ABC):
    @abstractmethod
    def operate(self) -> str:
        ...

class ReportBasicProduct(ReportProduct):
    def operate(self) -> str:
        return "basic-report"

class ReportPremiumProduct(ReportProduct):
    def operate(self) -> str:
        return "premium-report"

class ReportFactory:
    def create(self, type_name: str) -> ReportProduct:
        if not type_name:
            raise ValueError("type required")
        print(f"[log] create {type_name}")
        if type_name.lower() == "premium":
            return ReportPremiumProduct()
        return ReportBasicProduct()
