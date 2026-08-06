"""DesignPatternsSolid | kind=solid | label=lsp | domain=audio | tier=errors"""
from __future__ import annotations

from abc import ABC, abstractmethod

class AudioShape(ABC):
    @abstractmethod
    def area(self) -> int: ...

class AudioRectangle(AudioShape):
    def __init__(self, w: int, h: int) -> None:
        self.w = w
        self.h = h

    def area(self) -> int:
        return self.w * self.h

class AudioSquare(AudioShape):
    def __init__(self, side: int) -> None:
        self.side = side

    def area(self) -> int:
        return self.side * self.side

def total(shapes: list[AudioShape]) -> int:
    return sum(sh.area() for sh in shapes)
