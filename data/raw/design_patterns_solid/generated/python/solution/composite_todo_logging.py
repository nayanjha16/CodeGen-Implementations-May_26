"""DesignPatternsSolid | kind=design_pattern | label=composite | domain=todo | tier=logging"""
from __future__ import annotations

from abc import ABC, abstractmethod

class TodoNode(ABC):
    @abstractmethod
    def size(self) -> int: ...

class TodoLeaf(TodoNode):
    def __init__(self, weight: int) -> None:
        self.weight = weight

    def size(self) -> int:
        return self.weight

class TodoComposite(TodoNode):
    def __init__(self) -> None:
        self.children: list[TodoNode] = []

    def add(self, n: TodoNode) -> None:
        self.children.append(n)

    def size(self) -> int:
        return sum(n.size() for n in self.children)
