"""DesignPatternsSolid | kind=design_pattern | label=composite | domain=storage | tier=minimal"""
from __future__ import annotations

from abc import ABC, abstractmethod

class StorageNode(ABC):
    @abstractmethod
    def size(self) -> int: ...

class StorageLeaf(StorageNode):
    def __init__(self, weight: int) -> None:
        self.weight = weight

    def size(self) -> int:
        return self.weight

class StorageComposite(StorageNode):
    def __init__(self) -> None:
        self.children: list[StorageNode] = []

    def add(self, n: StorageNode) -> None:
        self.children.append(n)

    def size(self) -> int:
        return sum(n.size() for n in self.children)
