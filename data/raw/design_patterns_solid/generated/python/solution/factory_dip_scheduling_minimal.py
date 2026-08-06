"""DesignPatternsSolid | kind=combo | label=factory+dip | domain=scheduling | tier=minimal"""
from __future__ import annotations

from abc import ABC, abstractmethod

class SchedulingProduct(ABC):
    @abstractmethod
    def operate(self) -> str:
        ...

class SchedulingBasicProduct(SchedulingProduct):
    def operate(self) -> str:
        return "basic-scheduling"

class SchedulingPremiumProduct(SchedulingProduct):
    def operate(self) -> str:
        return "premium-scheduling"

class SchedulingFactory:
    def create(self, type_name: str) -> SchedulingProduct:
        if type_name.lower() == "premium":
            return SchedulingPremiumProduct()
        return SchedulingBasicProduct()
