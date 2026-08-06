"""DesignPatternsSolid | kind=design_pattern | label=composite | domain=widgets | tier=minimal"""
from __future__ import annotations

from abc import ABC, abstractmethod

class WidgetsNode(ABC):
    @abstractmethod
    def size(self) -> int: ...

class WidgetsLeaf(WidgetsNode):
    def __init__(self, weight: int) -> None:
        self.weight = weight

    def size(self) -> int:
        return self.weight

class WidgetsComposite(WidgetsNode):
    def __init__(self) -> None:
        self.children: list[WidgetsNode] = []

    def add(self, n: WidgetsNode) -> None:
        self.children.append(n)

    def size(self) -> int:
        return sum(n.size() for n in self.children)
