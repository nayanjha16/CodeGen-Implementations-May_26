"""DesignPatternsSolid | kind=combo | label=factory+dip | domain=analytics | tier=minimal"""
from __future__ import annotations

from abc import ABC, abstractmethod

class AnalyticsProduct(ABC):
    @abstractmethod
    def operate(self) -> str:
        ...

class AnalyticsBasicProduct(AnalyticsProduct):
    def operate(self) -> str:
        return "basic-analytics"

class AnalyticsPremiumProduct(AnalyticsProduct):
    def operate(self) -> str:
        return "premium-analytics"

class AnalyticsFactory:
    def create(self, type_name: str) -> AnalyticsProduct:
        if type_name.lower() == "premium":
            return AnalyticsPremiumProduct()
        return AnalyticsBasicProduct()
