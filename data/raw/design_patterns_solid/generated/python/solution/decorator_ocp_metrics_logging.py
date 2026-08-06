"""DesignPatternsSolid | kind=combo | label=decorator+ocp | domain=metrics | tier=logging"""
from __future__ import annotations

from abc import ABC, abstractmethod

class MetricsComponent(ABC):
    @abstractmethod
    def process(self, input: str) -> str: ...

class MetricsCore(MetricsComponent):
    def process(self, input: str) -> str:
        return f"metrics:{input}"

class MetricsUpperDecorator(MetricsComponent):
    def __init__(self, inner: MetricsComponent) -> None:
        self.inner = inner

    def process(self, input: str) -> str:
        return self.inner.process(input).upper()
