"""DesignPatternsSolid | kind=combo | label=decorator+ocp | domain=map | tier=minimal"""
from __future__ import annotations

from abc import ABC, abstractmethod

class MapComponent(ABC):
    @abstractmethod
    def process(self, input: str) -> str: ...

class MapCore(MapComponent):
    def process(self, input: str) -> str:
        return f"map:{input}"

class MapUpperDecorator(MapComponent):
    def __init__(self, inner: MapComponent) -> None:
        self.inner = inner

    def process(self, input: str) -> str:
        return self.inner.process(input).upper()
