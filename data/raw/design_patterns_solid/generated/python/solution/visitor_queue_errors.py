"""DesignPatternsSolid | kind=design_pattern | label=visitor | domain=queue | tier=errors"""
from __future__ import annotations

from abc import ABC, abstractmethod

class QueueVisitor(ABC):
    @abstractmethod
    def visit_leaf(self, leaf: "QueueLeaf") -> str: ...

class QueueElement(ABC):
    @abstractmethod
    def accept(self, v: QueueVisitor) -> str: ...

class QueueLeaf(QueueElement):
    def __init__(self, name: str) -> None:
        self.name = name

    def accept(self, v: QueueVisitor) -> str:
        return v.visit_leaf(self)

class QueuePrintVisitor(QueueVisitor):
    def visit_leaf(self, leaf: QueueLeaf) -> str:
        return f"queue:{leaf.name}"
