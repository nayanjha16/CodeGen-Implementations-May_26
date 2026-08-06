"""DesignPatternsSolid | kind=design_pattern | label=visitor | domain=notifications | tier=errors"""
from __future__ import annotations

from abc import ABC, abstractmethod

class NotificationsVisitor(ABC):
    @abstractmethod
    def visit_leaf(self, leaf: "NotificationsLeaf") -> str: ...

class NotificationsElement(ABC):
    @abstractmethod
    def accept(self, v: NotificationsVisitor) -> str: ...

class NotificationsLeaf(NotificationsElement):
    def __init__(self, name: str) -> None:
        self.name = name

    def accept(self, v: NotificationsVisitor) -> str:
        return v.visit_leaf(self)

class NotificationsPrintVisitor(NotificationsVisitor):
    def visit_leaf(self, leaf: NotificationsLeaf) -> str:
        return f"notifications:{leaf.name}"
