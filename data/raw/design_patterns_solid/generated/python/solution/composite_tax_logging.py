"""DesignPatternsSolid | kind=design_pattern | label=composite | domain=tax | tier=logging"""
from __future__ import annotations

from abc import ABC, abstractmethod

class TaxNode(ABC):
    @abstractmethod
    def size(self) -> int: ...

class TaxLeaf(TaxNode):
    def __init__(self, weight: int) -> None:
        self.weight = weight

    def size(self) -> int:
        return self.weight

class TaxComposite(TaxNode):
    def __init__(self) -> None:
        self.children: list[TaxNode] = []

    def add(self, n: TaxNode) -> None:
        self.children.append(n)

    def size(self) -> int:
        return sum(n.size() for n in self.children)
