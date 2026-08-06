"""DesignPatternsSolid | kind=solid | label=lsp | domain=notes | tier=errors"""
from __future__ import annotations

from abc import ABC, abstractmethod

class NotesShape(ABC):
    @abstractmethod
    def area(self) -> int: ...

class NotesRectangle(NotesShape):
    def __init__(self, w: int, h: int) -> None:
        self.w = w
        self.h = h

    def area(self) -> int:
        return self.w * self.h

class NotesSquare(NotesShape):
    def __init__(self, side: int) -> None:
        self.side = side

    def area(self) -> int:
        return self.side * self.side

def total(shapes: list[NotesShape]) -> int:
    return sum(sh.area() for sh in shapes)
