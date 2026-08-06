"""DesignPatternsSolid | kind=design_pattern | label=visitor | domain=backup | tier=minimal"""
from __future__ import annotations

from abc import ABC, abstractmethod

class BackupVisitor(ABC):
    @abstractmethod
    def visit_leaf(self, leaf: "BackupLeaf") -> str: ...

class BackupElement(ABC):
    @abstractmethod
    def accept(self, v: BackupVisitor) -> str: ...

class BackupLeaf(BackupElement):
    def __init__(self, name: str) -> None:
        self.name = name

    def accept(self, v: BackupVisitor) -> str:
        return v.visit_leaf(self)

class BackupPrintVisitor(BackupVisitor):
    def visit_leaf(self, leaf: BackupLeaf) -> str:
        return f"backup:{leaf.name}"
