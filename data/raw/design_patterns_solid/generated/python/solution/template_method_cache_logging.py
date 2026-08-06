"""DesignPatternsSolid | kind=design_pattern | label=template method | domain=cache | tier=logging"""
from __future__ import annotations

from abc import ABC, abstractmethod

class CacheTemplate(ABC):
    def run(self, input: str) -> str:
        prepared = self.prepare(input)
        processed = self.process(prepared)
        return self.finish(processed)

    def prepare(self, input: str) -> str:
        return input.strip()

    @abstractmethod
    def process(self, input: str) -> str: ...

    def finish(self, input: str) -> str:
        return f"cache|{input}"

class CacheUpperTemplate(CacheTemplate):
    def process(self, input: str) -> str:
        return input.upper()
