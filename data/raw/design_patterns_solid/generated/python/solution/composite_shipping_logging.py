"""DesignPatternsSolid | kind=design_pattern | label=composite | domain=shipping | tier=logging"""
from __future__ import annotations

from abc import ABC, abstractmethod

class ShippingNode(ABC):
    @abstractmethod
    def size(self) -> int: ...

class ShippingLeaf(ShippingNode):
    def __init__(self, weight: int) -> None:
        self.weight = weight

    def size(self) -> int:
        return self.weight

class ShippingComposite(ShippingNode):
    def __init__(self) -> None:
        self.children: list[ShippingNode] = []

    def add(self, n: ShippingNode) -> None:
        self.children.append(n)

    def size(self) -> int:
        return sum(n.size() for n in self.children)
