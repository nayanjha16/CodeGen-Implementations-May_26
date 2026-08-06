"""DesignPatternsSolid | kind=design_pattern | label=composite | domain=scheduling | tier=errors"""
from __future__ import annotations

from abc import ABC, abstractmethod

class SchedulingNode(ABC):
    @abstractmethod
    def size(self) -> int: ...

class SchedulingLeaf(SchedulingNode):
    def __init__(self, weight: int) -> None:
        self.weight = weight

    def size(self) -> int:
        return self.weight

class SchedulingComposite(SchedulingNode):
    def __init__(self) -> None:
        self.children: list[SchedulingNode] = []

    def add(self, n: SchedulingNode) -> None:
        self.children.append(n)

    def size(self) -> int:
        return sum(n.size() for n in self.children)
