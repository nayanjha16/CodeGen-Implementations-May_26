"""DesignPatternsSolid | kind=design_pattern | label=composite | domain=chat | tier=minimal"""
from __future__ import annotations

from abc import ABC, abstractmethod

class ChatNode(ABC):
    @abstractmethod
    def size(self) -> int: ...

class ChatLeaf(ChatNode):
    def __init__(self, weight: int) -> None:
        self.weight = weight

    def size(self) -> int:
        return self.weight

class ChatComposite(ChatNode):
    def __init__(self) -> None:
        self.children: list[ChatNode] = []

    def add(self, n: ChatNode) -> None:
        self.children.append(n)

    def size(self) -> int:
        return sum(n.size() for n in self.children)
