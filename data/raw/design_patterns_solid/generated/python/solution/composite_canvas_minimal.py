"""DesignPatternsSolid | kind=design_pattern | label=composite | domain=canvas | tier=minimal"""
from __future__ import annotations

from abc import ABC, abstractmethod

class CanvasNode(ABC):
    @abstractmethod
    def size(self) -> int: ...

class CanvasLeaf(CanvasNode):
    def __init__(self, weight: int) -> None:
        self.weight = weight

    def size(self) -> int:
        return self.weight

class CanvasComposite(CanvasNode):
    def __init__(self) -> None:
        self.children: list[CanvasNode] = []

    def add(self, n: CanvasNode) -> None:
        self.children.append(n)

    def size(self) -> int:
        return sum(n.size() for n in self.children)
