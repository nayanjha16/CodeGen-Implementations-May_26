"""DesignPatternsSolid | kind=design_pattern | label=composite | domain=discount | tier=logging"""
from __future__ import annotations

from abc import ABC, abstractmethod

class DiscountNode(ABC):
    @abstractmethod
    def size(self) -> int: ...

class DiscountLeaf(DiscountNode):
    def __init__(self, weight: int) -> None:
        self.weight = weight

    def size(self) -> int:
        return self.weight

class DiscountComposite(DiscountNode):
    def __init__(self) -> None:
        self.children: list[DiscountNode] = []

    def add(self, n: DiscountNode) -> None:
        self.children.append(n)

    def size(self) -> int:
        return sum(n.size() for n in self.children)
