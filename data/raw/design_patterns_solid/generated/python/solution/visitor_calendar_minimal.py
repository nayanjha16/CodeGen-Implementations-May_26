"""DesignPatternsSolid | kind=design_pattern | label=visitor | domain=calendar | tier=minimal"""
from __future__ import annotations

from abc import ABC, abstractmethod

class CalendarVisitor(ABC):
    @abstractmethod
    def visit_leaf(self, leaf: "CalendarLeaf") -> str: ...

class CalendarElement(ABC):
    @abstractmethod
    def accept(self, v: CalendarVisitor) -> str: ...

class CalendarLeaf(CalendarElement):
    def __init__(self, name: str) -> None:
        self.name = name

    def accept(self, v: CalendarVisitor) -> str:
        return v.visit_leaf(self)

class CalendarPrintVisitor(CalendarVisitor):
    def visit_leaf(self, leaf: CalendarLeaf) -> str:
        return f"calendar:{leaf.name}"
