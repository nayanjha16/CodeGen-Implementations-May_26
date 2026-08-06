"""DesignPatternsSolid | kind=design_pattern | label=visitor | domain=email | tier=minimal"""
from __future__ import annotations

from abc import ABC, abstractmethod

class EmailVisitor(ABC):
    @abstractmethod
    def visit_leaf(self, leaf: "EmailLeaf") -> str: ...

class EmailElement(ABC):
    @abstractmethod
    def accept(self, v: EmailVisitor) -> str: ...

class EmailLeaf(EmailElement):
    def __init__(self, name: str) -> None:
        self.name = name

    def accept(self, v: EmailVisitor) -> str:
        return v.visit_leaf(self)

class EmailPrintVisitor(EmailVisitor):
    def visit_leaf(self, leaf: EmailLeaf) -> str:
        return f"email:{leaf.name}"
