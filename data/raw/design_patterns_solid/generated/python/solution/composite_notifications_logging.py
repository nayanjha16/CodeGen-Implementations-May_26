"""DesignPatternsSolid | kind=design_pattern | label=composite | domain=notifications | tier=logging"""
from __future__ import annotations

from abc import ABC, abstractmethod

class NotificationsNode(ABC):
    @abstractmethod
    def size(self) -> int: ...

class NotificationsLeaf(NotificationsNode):
    def __init__(self, weight: int) -> None:
        self.weight = weight

    def size(self) -> int:
        return self.weight

class NotificationsComposite(NotificationsNode):
    def __init__(self) -> None:
        self.children: list[NotificationsNode] = []

    def add(self, n: NotificationsNode) -> None:
        self.children.append(n)

    def size(self) -> int:
        return sum(n.size() for n in self.children)
