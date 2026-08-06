"""DesignPatternsSolid | kind=combo | label=factory+dip | domain=map | tier=minimal"""
from __future__ import annotations

from abc import ABC, abstractmethod

class MapProduct(ABC):
    @abstractmethod
    def operate(self) -> str:
        ...

class MapBasicProduct(MapProduct):
    def operate(self) -> str:
        return "basic-map"

class MapPremiumProduct(MapProduct):
    def operate(self) -> str:
        return "premium-map"

class MapFactory:
    def create(self, type_name: str) -> MapProduct:
        if type_name.lower() == "premium":
            return MapPremiumProduct()
        return MapBasicProduct()
