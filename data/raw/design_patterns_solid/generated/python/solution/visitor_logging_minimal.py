"""DesignPatternsSolid | kind=design_pattern | label=visitor | domain=logging | tier=minimal"""
from __future__ import annotations

from abc import ABC, abstractmethod

class LoggingVisitor(ABC):
    @abstractmethod
    def visit_leaf(self, leaf: "LoggingLeaf") -> str: ...

class LoggingElement(ABC):
    @abstractmethod
    def accept(self, v: LoggingVisitor) -> str: ...

class LoggingLeaf(LoggingElement):
    def __init__(self, name: str) -> None:
        self.name = name

    def accept(self, v: LoggingVisitor) -> str:
        return v.visit_leaf(self)

class LoggingPrintVisitor(LoggingVisitor):
    def visit_leaf(self, leaf: LoggingLeaf) -> str:
        return f"logging:{leaf.name}"
