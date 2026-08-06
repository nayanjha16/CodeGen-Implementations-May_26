"""DesignPatternsSolid | kind=combo | label=factory+dip | domain=feed | tier=logging"""
from __future__ import annotations

from abc import ABC, abstractmethod

class FeedProduct(ABC):
    @abstractmethod
    def operate(self) -> str:
        ...

class FeedBasicProduct(FeedProduct):
    def operate(self) -> str:
        return "basic-feed"

class FeedPremiumProduct(FeedProduct):
    def operate(self) -> str:
        return "premium-feed"

class FeedFactory:
    def create(self, type_name: str) -> FeedProduct:
        print(f"[log] create {type_name}")
        if type_name.lower() == "premium":
            return FeedPremiumProduct()
        return FeedBasicProduct()
