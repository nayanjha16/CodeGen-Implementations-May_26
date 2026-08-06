"""DesignPatternsSolid | kind=design_pattern | label=composite | domain=game | tier=errors"""
from __future__ import annotations

from abc import ABC, abstractmethod

class GameNode(ABC):
    @abstractmethod
    def size(self) -> int: ...

class GameLeaf(GameNode):
    def __init__(self, weight: int) -> None:
        self.weight = weight

    def size(self) -> int:
        return self.weight

class GameComposite(GameNode):
    def __init__(self) -> None:
        self.children: list[GameNode] = []

    def add(self, n: GameNode) -> None:
        self.children.append(n)

    def size(self) -> int:
        return sum(n.size() for n in self.children)
