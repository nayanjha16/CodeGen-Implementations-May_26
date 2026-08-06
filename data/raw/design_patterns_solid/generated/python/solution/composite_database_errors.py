"""DesignPatternsSolid | kind=design_pattern | label=composite | domain=database | tier=errors"""
from __future__ import annotations

from abc import ABC, abstractmethod

class DatabaseNode(ABC):
    @abstractmethod
    def size(self) -> int: ...

class DatabaseLeaf(DatabaseNode):
    def __init__(self, weight: int) -> None:
        self.weight = weight

    def size(self) -> int:
        return self.weight

class DatabaseComposite(DatabaseNode):
    def __init__(self) -> None:
        self.children: list[DatabaseNode] = []

    def add(self, n: DatabaseNode) -> None:
        self.children.append(n)

    def size(self) -> int:
        return sum(n.size() for n in self.children)
