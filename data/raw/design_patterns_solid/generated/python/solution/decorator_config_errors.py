"""DesignPatternsSolid | kind=design_pattern | label=decorator | domain=config | tier=errors"""
from __future__ import annotations

from abc import ABC, abstractmethod

class ConfigComponent(ABC):
    @abstractmethod
    def process(self, input: str) -> str: ...

class ConfigCore(ConfigComponent):
    def process(self, input: str) -> str:
        return f"config:{input}"

class ConfigUpperDecorator(ConfigComponent):
    def __init__(self, inner: ConfigComponent) -> None:
        self.inner = inner

    def process(self, input: str) -> str:
        return self.inner.process(input).upper()
