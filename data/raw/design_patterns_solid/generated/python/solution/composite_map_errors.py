"""DesignPatternsSolid | kind=design_pattern | label=composite | domain=map | tier=errors"""
from __future__ import annotations

from abc import ABC, abstractmethod

class MapNode(ABC):
    @abstractmethod
    def size(self) -> int: ...

class MapLeaf(MapNode):
    def __init__(self, weight: int) -> None:
        self.weight = weight

    def size(self) -> int:
        return self.weight

class MapComposite(MapNode):
    def __init__(self) -> None:
        self.children: list[MapNode] = []

    def add(self, n: MapNode) -> None:
        self.children.append(n)

    def size(self) -> int:
        return sum(n.size() for n in self.children)
