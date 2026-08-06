"""DesignPatternsSolid | kind=design_pattern | label=composite | domain=billing | tier=errors"""
from __future__ import annotations

from abc import ABC, abstractmethod

class BillingNode(ABC):
    @abstractmethod
    def size(self) -> int: ...

class BillingLeaf(BillingNode):
    def __init__(self, weight: int) -> None:
        self.weight = weight

    def size(self) -> int:
        return self.weight

class BillingComposite(BillingNode):
    def __init__(self) -> None:
        self.children: list[BillingNode] = []

    def add(self, n: BillingNode) -> None:
        self.children.append(n)

    def size(self) -> int:
        return sum(n.size() for n in self.children)
