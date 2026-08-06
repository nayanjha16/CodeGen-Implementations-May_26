"""DesignPatternsSolid | kind=design_pattern | label=composite | domain=ticket | tier=minimal"""
from __future__ import annotations

from abc import ABC, abstractmethod

class TicketNode(ABC):
    @abstractmethod
    def size(self) -> int: ...

class TicketLeaf(TicketNode):
    def __init__(self, weight: int) -> None:
        self.weight = weight

    def size(self) -> int:
        return self.weight

class TicketComposite(TicketNode):
    def __init__(self) -> None:
        self.children: list[TicketNode] = []

    def add(self, n: TicketNode) -> None:
        self.children.append(n)

    def size(self) -> int:
        return sum(n.size() for n in self.children)
