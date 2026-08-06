"""DesignPatternsSolid | kind=design_pattern | label=composite | domain=http | tier=errors"""
from __future__ import annotations

from abc import ABC, abstractmethod

class HttpNode(ABC):
    @abstractmethod
    def size(self) -> int: ...

class HttpLeaf(HttpNode):
    def __init__(self, weight: int) -> None:
        self.weight = weight

    def size(self) -> int:
        return self.weight

class HttpComposite(HttpNode):
    def __init__(self) -> None:
        self.children: list[HttpNode] = []

    def add(self, n: HttpNode) -> None:
        self.children.append(n)

    def size(self) -> int:
        return sum(n.size() for n in self.children)
