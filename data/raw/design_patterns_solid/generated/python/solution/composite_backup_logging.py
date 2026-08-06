"""DesignPatternsSolid | kind=design_pattern | label=composite | domain=backup | tier=logging"""
from __future__ import annotations

from abc import ABC, abstractmethod

class BackupNode(ABC):
    @abstractmethod
    def size(self) -> int: ...

class BackupLeaf(BackupNode):
    def __init__(self, weight: int) -> None:
        self.weight = weight

    def size(self) -> int:
        return self.weight

class BackupComposite(BackupNode):
    def __init__(self) -> None:
        self.children: list[BackupNode] = []

    def add(self, n: BackupNode) -> None:
        self.children.append(n)

    def size(self) -> int:
        return sum(n.size() for n in self.children)
