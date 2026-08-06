"""DesignPatternsSolid | kind=design_pattern | label=composite | domain=cart | tier=logging"""
from __future__ import annotations

from abc import ABC, abstractmethod

class CartNode(ABC):
    @abstractmethod
    def size(self) -> int: ...

class CartLeaf(CartNode):
    def __init__(self, weight: int) -> None:
        self.weight = weight

    def size(self) -> int:
        return self.weight

class CartComposite(CartNode):
    def __init__(self) -> None:
        self.children: list[CartNode] = []

    def add(self, n: CartNode) -> None:
        self.children.append(n)

    def size(self) -> int:
        return sum(n.size() for n in self.children)
