"""DesignPatternsSolid | kind=design_pattern | label=composite | domain=search | tier=logging"""
from __future__ import annotations

from abc import ABC, abstractmethod

class SearchNode(ABC):
    @abstractmethod
    def size(self) -> int: ...

class SearchLeaf(SearchNode):
    def __init__(self, weight: int) -> None:
        self.weight = weight

    def size(self) -> int:
        return self.weight

class SearchComposite(SearchNode):
    def __init__(self) -> None:
        self.children: list[SearchNode] = []

    def add(self, n: SearchNode) -> None:
        self.children.append(n)

    def size(self) -> int:
        return sum(n.size() for n in self.children)
