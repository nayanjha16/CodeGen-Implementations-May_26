"""DesignPatternsSolid | kind=design_pattern | label=visitor | domain=comment | tier=logging"""
from __future__ import annotations

from abc import ABC, abstractmethod

class CommentVisitor(ABC):
    @abstractmethod
    def visit_leaf(self, leaf: "CommentLeaf") -> str: ...

class CommentElement(ABC):
    @abstractmethod
    def accept(self, v: CommentVisitor) -> str: ...

class CommentLeaf(CommentElement):
    def __init__(self, name: str) -> None:
        self.name = name

    def accept(self, v: CommentVisitor) -> str:
        return v.visit_leaf(self)

class CommentPrintVisitor(CommentVisitor):
    def visit_leaf(self, leaf: CommentLeaf) -> str:
        return f"comment:{leaf.name}"
