"""DesignPatternsSolid | kind=design_pattern | label=visitor | domain=sync | tier=minimal"""
from __future__ import annotations

from abc import ABC, abstractmethod

class SyncVisitor(ABC):
    @abstractmethod
    def visit_leaf(self, leaf: "SyncLeaf") -> str: ...

class SyncElement(ABC):
    @abstractmethod
    def accept(self, v: SyncVisitor) -> str: ...

class SyncLeaf(SyncElement):
    def __init__(self, name: str) -> None:
        self.name = name

    def accept(self, v: SyncVisitor) -> str:
        return v.visit_leaf(self)

class SyncPrintVisitor(SyncVisitor):
    def visit_leaf(self, leaf: SyncLeaf) -> str:
        return f"sync:{leaf.name}"
