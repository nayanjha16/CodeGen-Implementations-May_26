"""DesignPatternsSolid | kind=design_pattern | label=visitor | domain=streaming | tier=logging"""
from __future__ import annotations

from abc import ABC, abstractmethod

class StreamingVisitor(ABC):
    @abstractmethod
    def visit_leaf(self, leaf: "StreamingLeaf") -> str: ...

class StreamingElement(ABC):
    @abstractmethod
    def accept(self, v: StreamingVisitor) -> str: ...

class StreamingLeaf(StreamingElement):
    def __init__(self, name: str) -> None:
        self.name = name

    def accept(self, v: StreamingVisitor) -> str:
        return v.visit_leaf(self)

class StreamingPrintVisitor(StreamingVisitor):
    def visit_leaf(self, leaf: StreamingLeaf) -> str:
        return f"streaming:{leaf.name}"
