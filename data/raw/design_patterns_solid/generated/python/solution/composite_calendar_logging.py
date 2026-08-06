"""DesignPatternsSolid | kind=design_pattern | label=composite | domain=calendar | tier=logging"""
from __future__ import annotations

from abc import ABC, abstractmethod

class CalendarNode(ABC):
    @abstractmethod
    def size(self) -> int: ...

class CalendarLeaf(CalendarNode):
    def __init__(self, weight: int) -> None:
        self.weight = weight

    def size(self) -> int:
        return self.weight

class CalendarComposite(CalendarNode):
    def __init__(self) -> None:
        self.children: list[CalendarNode] = []

    def add(self, n: CalendarNode) -> None:
        self.children.append(n)

    def size(self) -> int:
        return sum(n.size() for n in self.children)
