"""DesignPatternsSolid | kind=design_pattern | label=decorator | domain=cache | tier=errors"""
from __future__ import annotations

from abc import ABC, abstractmethod

class CacheComponent(ABC):
    @abstractmethod
    def process(self, input: str) -> str: ...

class CacheCore(CacheComponent):
    def process(self, input: str) -> str:
        return f"cache:{input}"

class CacheUpperDecorator(CacheComponent):
    def __init__(self, inner: CacheComponent) -> None:
        self.inner = inner

    def process(self, input: str) -> str:
        return self.inner.process(input).upper()
