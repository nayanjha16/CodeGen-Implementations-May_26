"""DesignPatternsSolid | kind=design_pattern | label=composite | domain=cache | tier=errors"""
from __future__ import annotations

from abc import ABC, abstractmethod

class CacheNode(ABC):
    @abstractmethod
    def size(self) -> int: ...

class CacheLeaf(CacheNode):
    def __init__(self, weight: int) -> None:
        self.weight = weight

    def size(self) -> int:
        return self.weight

class CacheComposite(CacheNode):
    def __init__(self) -> None:
        self.children: list[CacheNode] = []

    def add(self, n: CacheNode) -> None:
        self.children.append(n)

    def size(self) -> int:
        return sum(n.size() for n in self.children)
