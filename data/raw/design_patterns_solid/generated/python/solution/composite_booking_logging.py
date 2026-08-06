"""DesignPatternsSolid | kind=design_pattern | label=composite | domain=booking | tier=logging"""
from __future__ import annotations

from abc import ABC, abstractmethod

class BookingNode(ABC):
    @abstractmethod
    def size(self) -> int: ...

class BookingLeaf(BookingNode):
    def __init__(self, weight: int) -> None:
        self.weight = weight

    def size(self) -> int:
        return self.weight

class BookingComposite(BookingNode):
    def __init__(self) -> None:
        self.children: list[BookingNode] = []

    def add(self, n: BookingNode) -> None:
        self.children.append(n)

    def size(self) -> int:
        return sum(n.size() for n in self.children)
