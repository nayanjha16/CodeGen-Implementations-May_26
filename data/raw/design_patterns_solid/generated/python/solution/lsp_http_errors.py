"""DesignPatternsSolid | kind=solid | label=lsp | domain=http | tier=errors"""
from __future__ import annotations

from abc import ABC, abstractmethod

class HttpShape(ABC):
    @abstractmethod
    def area(self) -> int: ...

class HttpRectangle(HttpShape):
    def __init__(self, w: int, h: int) -> None:
        self.w = w
        self.h = h

    def area(self) -> int:
        return self.w * self.h

class HttpSquare(HttpShape):
    def __init__(self, side: int) -> None:
        self.side = side

    def area(self) -> int:
        return self.side * self.side

def total(shapes: list[HttpShape]) -> int:
    return sum(sh.area() for sh in shapes)
