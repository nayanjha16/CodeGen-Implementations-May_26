"""DesignPatternsSolid | kind=design_pattern | label=visitor | domain=todo | tier=errors"""
from __future__ import annotations

from abc import ABC, abstractmethod

class TodoVisitor(ABC):
    @abstractmethod
    def visit_leaf(self, leaf: "TodoLeaf") -> str: ...

class TodoElement(ABC):
    @abstractmethod
    def accept(self, v: TodoVisitor) -> str: ...

class TodoLeaf(TodoElement):
    def __init__(self, name: str) -> None:
        self.name = name

    def accept(self, v: TodoVisitor) -> str:
        return v.visit_leaf(self)

class TodoPrintVisitor(TodoVisitor):
    def visit_leaf(self, leaf: TodoLeaf) -> str:
        return f"todo:{leaf.name}"
