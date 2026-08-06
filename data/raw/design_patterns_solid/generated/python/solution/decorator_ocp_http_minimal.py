"""DesignPatternsSolid | kind=combo | label=decorator+ocp | domain=http | tier=minimal"""
from __future__ import annotations

from abc import ABC, abstractmethod

class HttpComponent(ABC):
    @abstractmethod
    def process(self, input: str) -> str: ...

class HttpCore(HttpComponent):
    def process(self, input: str) -> str:
        return f"http:{input}"

class HttpUpperDecorator(HttpComponent):
    def __init__(self, inner: HttpComponent) -> None:
        self.inner = inner

    def process(self, input: str) -> str:
        return self.inner.process(input).upper()
