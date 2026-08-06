"""DesignPatternsSolid | kind=design_pattern | label=visitor | domain=session | tier=errors"""
from __future__ import annotations

from abc import ABC, abstractmethod

class SessionVisitor(ABC):
    @abstractmethod
    def visit_leaf(self, leaf: "SessionLeaf") -> str: ...

class SessionElement(ABC):
    @abstractmethod
    def accept(self, v: SessionVisitor) -> str: ...

class SessionLeaf(SessionElement):
    def __init__(self, name: str) -> None:
        self.name = name

    def accept(self, v: SessionVisitor) -> str:
        return v.visit_leaf(self)

class SessionPrintVisitor(SessionVisitor):
    def visit_leaf(self, leaf: SessionLeaf) -> str:
        return f"session:{leaf.name}"
