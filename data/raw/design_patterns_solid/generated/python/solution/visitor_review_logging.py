"""DesignPatternsSolid | kind=design_pattern | label=visitor | domain=review | tier=logging"""
from __future__ import annotations

from abc import ABC, abstractmethod

class ReviewVisitor(ABC):
    @abstractmethod
    def visit_leaf(self, leaf: "ReviewLeaf") -> str: ...

class ReviewElement(ABC):
    @abstractmethod
    def accept(self, v: ReviewVisitor) -> str: ...

class ReviewLeaf(ReviewElement):
    def __init__(self, name: str) -> None:
        self.name = name

    def accept(self, v: ReviewVisitor) -> str:
        return v.visit_leaf(self)

class ReviewPrintVisitor(ReviewVisitor):
    def visit_leaf(self, leaf: ReviewLeaf) -> str:
        return f"review:{leaf.name}"
