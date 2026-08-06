"""DesignPatternsSolid | kind=combo | label=factory+dip | domain=review | tier=minimal"""
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
        if type_name.lower() == "premium":
            return ReviewPremiumProduct()
        return ReviewBasicProduct()
