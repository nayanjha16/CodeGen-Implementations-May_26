"""DesignPatternsSolid | kind=design_pattern | label=decorator | domain=analytics | tier=minimal"""
from __future__ import annotations

from abc import ABC, abstractmethod

class AnalyticsComponent(ABC):
    @abstractmethod
    def process(self, input: str) -> str: ...

class AnalyticsCore(AnalyticsComponent):
    def process(self, input: str) -> str:
        return f"analytics:{input}"

class AnalyticsUpperDecorator(AnalyticsComponent):
    def __init__(self, inner: AnalyticsComponent) -> None:
        self.inner = inner

    def process(self, input: str) -> str:
        return self.inner.process(input).upper()
