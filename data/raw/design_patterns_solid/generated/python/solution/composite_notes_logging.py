"""DesignPatternsSolid | kind=design_pattern | label=composite | domain=notes | tier=logging"""
from __future__ import annotations

from abc import ABC, abstractmethod

class NotesNode(ABC):
    @abstractmethod
    def size(self) -> int: ...

class NotesLeaf(NotesNode):
    def __init__(self, weight: int) -> None:
        self.weight = weight

    def size(self) -> int:
        return self.weight

class NotesComposite(NotesNode):
    def __init__(self) -> None:
        self.children: list[NotesNode] = []

    def add(self, n: NotesNode) -> None:
        self.children.append(n)

    def size(self) -> int:
        return sum(n.size() for n in self.children)
