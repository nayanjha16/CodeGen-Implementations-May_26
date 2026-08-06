"""DesignPatternsSolid | kind=solid | label=lsp | domain=cache | tier=logging"""
from __future__ import annotations

from abc import ABC, abstractmethod

class CacheShape(ABC):
    @abstractmethod
    def area(self) -> int: ...

class CacheRectangle(CacheShape):
    def __init__(self, w: int, h: int) -> None:
        self.w = w
        self.h = h

    def area(self) -> int:
        return self.w * self.h

class CacheSquare(CacheShape):
    def __init__(self, side: int) -> None:
        self.side = side

    def area(self) -> int:
        return self.side * self.side

def total(shapes: list[CacheShape]) -> int:
    return sum(sh.area() for sh in shapes)
