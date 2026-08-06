"""DesignPatternsSolid | kind=design_pattern | label=composite | domain=analytics | tier=logging"""
from __future__ import annotations

from abc import ABC, abstractmethod

class AnalyticsNode(ABC):
    @abstractmethod
    def size(self) -> int: ...

class AnalyticsLeaf(AnalyticsNode):
    def __init__(self, weight: int) -> None:
        self.weight = weight

    def size(self) -> int:
        return self.weight

class AnalyticsComposite(AnalyticsNode):
    def __init__(self) -> None:
        self.children: list[AnalyticsNode] = []

    def add(self, n: AnalyticsNode) -> None:
        self.children.append(n)

    def size(self) -> int:
        return sum(n.size() for n in self.children)
