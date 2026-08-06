"""DesignPatternsSolid | kind=combo | label=factory+dip | domain=sensors | tier=logging"""
from __future__ import annotations

from abc import ABC, abstractmethod

class SensorsProduct(ABC):
    @abstractmethod
    def operate(self) -> str:
        ...

class SensorsBasicProduct(SensorsProduct):
    def operate(self) -> str:
        return "basic-sensors"

class SensorsPremiumProduct(SensorsProduct):
    def operate(self) -> str:
        return "premium-sensors"

class SensorsFactory:
    def create(self, type_name: str) -> SensorsProduct:
        print(f"[log] create {type_name}")
        if type_name.lower() == "premium":
            return SensorsPremiumProduct()
        return SensorsBasicProduct()
