"""DesignPatternsSolid | kind=design_pattern | label=composite | domain=session | tier=logging"""
from __future__ import annotations

from abc import ABC, abstractmethod

class SessionNode(ABC):
    @abstractmethod
    def size(self) -> int: ...

class SessionLeaf(SessionNode):
    def __init__(self, weight: int) -> None:
        self.weight = weight

    def size(self) -> int:
        return self.weight

class SessionComposite(SessionNode):
    def __init__(self) -> None:
        self.children: list[SessionNode] = []

    def add(self, n: SessionNode) -> None:
        self.children.append(n)

    def size(self) -> int:
        return sum(n.size() for n in self.children)
