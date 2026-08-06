"""DesignPatternsSolid | kind=design_pattern | label=composite | domain=sms | tier=errors"""
from __future__ import annotations

from abc import ABC, abstractmethod

class SmsNode(ABC):
    @abstractmethod
    def size(self) -> int: ...

class SmsLeaf(SmsNode):
    def __init__(self, weight: int) -> None:
        self.weight = weight

    def size(self) -> int:
        return self.weight

class SmsComposite(SmsNode):
    def __init__(self) -> None:
        self.children: list[SmsNode] = []

    def add(self, n: SmsNode) -> None:
        self.children.append(n)

    def size(self) -> int:
        return sum(n.size() for n in self.children)
