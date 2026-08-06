"""DesignPatternsSolid | kind=design_pattern | label=decorator | domain=search | tier=logging"""
from __future__ import annotations

from abc import ABC, abstractmethod

class SearchComponent(ABC):
    @abstractmethod
    def process(self, input: str) -> str: ...

class SearchCore(SearchComponent):
    def process(self, input: str) -> str:
        return f"search:{input}"

class SearchUpperDecorator(SearchComponent):
    def __init__(self, inner: SearchComponent) -> None:
        self.inner = inner

    def process(self, input: str) -> str:
        return self.inner.process(input).upper()
