"""DesignPatternsSolid | kind=design_pattern | label=visitor | domain=notes | tier=logging"""
from __future__ import annotations

from abc import ABC, abstractmethod

class NotesVisitor(ABC):
    @abstractmethod
    def visit_leaf(self, leaf: "NotesLeaf") -> str: ...

class NotesElement(ABC):
    @abstractmethod
    def accept(self, v: NotesVisitor) -> str: ...

class NotesLeaf(NotesElement):
    def __init__(self, name: str) -> None:
        self.name = name

    def accept(self, v: NotesVisitor) -> str:
        return v.visit_leaf(self)

class NotesPrintVisitor(NotesVisitor):
    def visit_leaf(self, leaf: NotesLeaf) -> str:
        return f"notes:{leaf.name}"
