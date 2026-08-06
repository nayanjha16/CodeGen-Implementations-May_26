"""DesignPatternsSolid | kind=design_pattern | label=composite | domain=plugin | tier=minimal"""
from __future__ import annotations

from abc import ABC, abstractmethod

class PluginNode(ABC):
    @abstractmethod
    def size(self) -> int: ...

class PluginLeaf(PluginNode):
    def __init__(self, weight: int) -> None:
        self.weight = weight

    def size(self) -> int:
        return self.weight

class PluginComposite(PluginNode):
    def __init__(self) -> None:
        self.children: list[PluginNode] = []

    def add(self, n: PluginNode) -> None:
        self.children.append(n)

    def size(self) -> int:
        return sum(n.size() for n in self.children)
