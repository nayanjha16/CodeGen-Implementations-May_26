"""DesignPatternsSolid | kind=design_pattern | label=factory | domain=review | tier=logging"""
from __future__ import annotations

from abc import ABC, abstractmethod

class ReviewProduct(ABC):
    @abstractmethod
    def operate(self) -> str:
        ...

class ReviewBasicProduct(ReviewProduct):
    def operate(self) -> str:
        return "basic-review"

class ReviewPremiumProduct(ReviewProduct):
    def operate(self) -> str:
        return "premium-review"

class ReviewFactory:
    def create(self, type_name: str) -> ReviewProduct:
        print(f"[log] create {type_name}")
        if type_name.lower() == "premium":
            return ReviewPremiumProduct()
        return ReviewBasicProduct()
