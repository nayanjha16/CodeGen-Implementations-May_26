"""DesignPatternsSolid | kind=design_pattern | label=composite | domain=logging | tier=errors"""
from __future__ import annotations

from abc import ABC, abstractmethod

class LoggingNode(ABC):
    @abstractmethod
    def size(self) -> int: ...

class LoggingLeaf(LoggingNode):
    def __init__(self, weight: int) -> None:
        self.weight = weight

    def size(self) -> int:
        return self.weight

class LoggingComposite(LoggingNode):
    def __init__(self) -> None:
        self.children: list[LoggingNode] = []

    def add(self, n: LoggingNode) -> None:
        self.children.append(n)

    def size(self) -> int:
        return sum(n.size() for n in self.children)
