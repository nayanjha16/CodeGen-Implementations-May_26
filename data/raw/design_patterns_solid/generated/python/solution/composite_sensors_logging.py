"""DesignPatternsSolid | kind=design_pattern | label=composite | domain=sensors | tier=logging"""
from __future__ import annotations

from abc import ABC, abstractmethod

class SensorsNode(ABC):
    @abstractmethod
    def size(self) -> int: ...

class SensorsLeaf(SensorsNode):
    def __init__(self, weight: int) -> None:
        self.weight = weight

    def size(self) -> int:
        return self.weight

class SensorsComposite(SensorsNode):
    def __init__(self) -> None:
        self.children: list[SensorsNode] = []

    def add(self, n: SensorsNode) -> None:
        self.children.append(n)

    def size(self) -> int:
        return sum(n.size() for n in self.children)
