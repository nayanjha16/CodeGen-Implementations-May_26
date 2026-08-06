"""DesignPatternsSolid | kind=combo | label=factory+dip | domain=comment | tier=minimal"""
from __future__ import annotations

from abc import ABC, abstractmethod

class CommentProduct(ABC):
    @abstractmethod
    def operate(self) -> str:
        ...

class CommentBasicProduct(CommentProduct):
    def operate(self) -> str:
        return "basic-comment"

class CommentPremiumProduct(CommentProduct):
    def operate(self) -> str:
        return "premium-comment"

class CommentFactory:
    def create(self, type_name: str) -> CommentProduct:
        if type_name.lower() == "premium":
            return CommentPremiumProduct()
        return CommentBasicProduct()
