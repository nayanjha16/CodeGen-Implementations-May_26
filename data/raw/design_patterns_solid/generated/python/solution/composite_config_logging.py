"""DesignPatternsSolid | kind=design_pattern | label=composite | domain=config | tier=logging"""
from __future__ import annotations

from abc import ABC, abstractmethod

class ConfigNode(ABC):
    @abstractmethod
    def size(self) -> int: ...

class ConfigLeaf(ConfigNode):
    def __init__(self, weight: int) -> None:
        self.weight = weight

    def size(self) -> int:
        return self.weight

class ConfigComposite(ConfigNode):
    def __init__(self) -> None:
        self.children: list[ConfigNode] = []

    def add(self, n: ConfigNode) -> None:
        self.children.append(n)

    def size(self) -> int:
        return sum(n.size() for n in self.children)
