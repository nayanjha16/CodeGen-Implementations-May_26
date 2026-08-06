"""DesignPatternsSolid | kind=combo | label=factory+dip | domain=metrics | tier=minimal"""
from __future__ import annotations

from abc import ABC, abstractmethod

class MetricsProduct(ABC):
    @abstractmethod
    def operate(self) -> str:
        ...

class MetricsBasicProduct(MetricsProduct):
    def operate(self) -> str:
        return "basic-metrics"

class MetricsPremiumProduct(MetricsProduct):
    def operate(self) -> str:
        return "premium-metrics"

class MetricsFactory:
    def create(self, type_name: str) -> MetricsProduct:
        if type_name.lower() == "premium":
            return MetricsPremiumProduct()
        return MetricsBasicProduct()
