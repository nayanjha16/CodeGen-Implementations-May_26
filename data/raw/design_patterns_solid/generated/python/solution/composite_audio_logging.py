"""DesignPatternsSolid | kind=design_pattern | label=composite | domain=audio | tier=logging"""
from __future__ import annotations

from abc import ABC, abstractmethod

class AudioNode(ABC):
    @abstractmethod
    def size(self) -> int: ...

class AudioLeaf(AudioNode):
    def __init__(self, weight: int) -> None:
        self.weight = weight

    def size(self) -> int:
        return self.weight

class AudioComposite(AudioNode):
    def __init__(self) -> None:
        self.children: list[AudioNode] = []

    def add(self, n: AudioNode) -> None:
        self.children.append(n)

    def size(self) -> int:
        return sum(n.size() for n in self.children)
