"""DesignPatternsSolid | kind=design_pattern | label=composite | domain=streaming | tier=errors"""
from __future__ import annotations

from abc import ABC, abstractmethod

class StreamingNode(ABC):
    @abstractmethod
    def size(self) -> int: ...

class StreamingLeaf(StreamingNode):
    def __init__(self, weight: int) -> None:
        self.weight = weight

    def size(self) -> int:
        return self.weight

class StreamingComposite(StreamingNode):
    def __init__(self) -> None:
        self.children: list[StreamingNode] = []

    def add(self, n: StreamingNode) -> None:
        self.children.append(n)

    def size(self) -> int:
        return sum(n.size() for n in self.children)
