"""DesignPatternsSolid | kind=design_pattern | label=visitor | domain=report | tier=minimal"""
from __future__ import annotations

from abc import ABC, abstractmethod

class ReportVisitor(ABC):
    @abstractmethod
    def visit_leaf(self, leaf: "ReportLeaf") -> str: ...

class ReportElement(ABC):
    @abstractmethod
    def accept(self, v: ReportVisitor) -> str: ...

class ReportLeaf(ReportElement):
    def __init__(self, name: str) -> None:
        self.name = name

    def accept(self, v: ReportVisitor) -> str:
        return v.visit_leaf(self)

class ReportPrintVisitor(ReportVisitor):
    def visit_leaf(self, leaf: ReportLeaf) -> str:
        return f"report:{leaf.name}"
