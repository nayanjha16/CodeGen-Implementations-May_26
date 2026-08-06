"""DesignPatternsSolid | kind=combo | label=decorator+ocp | domain=widgets | tier=errors"""
from __future__ import annotations

from abc import ABC, abstractmethod

class WidgetsComponent(ABC):
    @abstractmethod
    def process(self, input: str) -> str: ...

class WidgetsCore(WidgetsComponent):
    def process(self, input: str) -> str:
        return f"widgets:{input}"

class WidgetsUpperDecorator(WidgetsComponent):
    def __init__(self, inner: WidgetsComponent) -> None:
        self.inner = inner

    def process(self, input: str) -> str:
        return self.inner.process(input).upper()
