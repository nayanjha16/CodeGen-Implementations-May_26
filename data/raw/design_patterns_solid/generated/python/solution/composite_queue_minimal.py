"""DesignPatternsSolid | kind=design_pattern | label=composite | domain=queue | tier=minimal"""
from __future__ import annotations

from abc import ABC, abstractmethod

class QueueNode(ABC):
    @abstractmethod
    def size(self) -> int: ...

class QueueLeaf(QueueNode):
    def __init__(self, weight: int) -> None:
        self.weight = weight

    def size(self) -> int:
        return self.weight

class QueueComposite(QueueNode):
    def __init__(self) -> None:
        self.children: list[QueueNode] = []

    def add(self, n: QueueNode) -> None:
        self.children.append(n)

    def size(self) -> int:
        return sum(n.size() for n in self.children)
