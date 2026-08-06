"""DesignPatternsSolid | kind=design_pattern | label=visitor | domain=http | tier=logging"""
from __future__ import annotations

from abc import ABC, abstractmethod

class HttpVisitor(ABC):
    @abstractmethod
    def visit_leaf(self, leaf: "HttpLeaf") -> str: ...

class HttpElement(ABC):
    @abstractmethod
    def accept(self, v: HttpVisitor) -> str: ...

class HttpLeaf(HttpElement):
    def __init__(self, name: str) -> None:
        self.name = name

    def accept(self, v: HttpVisitor) -> str:
        return v.visit_leaf(self)

class HttpPrintVisitor(HttpVisitor):
    def visit_leaf(self, leaf: HttpLeaf) -> str:
        return f"http:{leaf.name}"
