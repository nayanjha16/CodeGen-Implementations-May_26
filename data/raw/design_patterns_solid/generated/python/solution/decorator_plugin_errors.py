"""DesignPatternsSolid | kind=design_pattern | label=decorator | domain=plugin | tier=errors"""
from __future__ import annotations

from abc import ABC, abstractmethod

class PluginComponent(ABC):
    @abstractmethod
    def process(self, input: str) -> str: ...

class PluginCore(PluginComponent):
    def process(self, input: str) -> str:
        return f"plugin:{input}"

class PluginUpperDecorator(PluginComponent):
    def __init__(self, inner: PluginComponent) -> None:
        self.inner = inner

    def process(self, input: str) -> str:
        return self.inner.process(input).upper()
