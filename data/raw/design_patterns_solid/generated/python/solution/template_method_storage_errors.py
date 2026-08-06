"""DesignPatternsSolid | kind=design_pattern | label=template method | domain=storage | tier=errors"""
from __future__ import annotations

from abc import ABC, abstractmethod

class StorageTemplate(ABC):
    def run(self, input: str) -> str:
        prepared = self.prepare(input)
        processed = self.process(prepared)
        return self.finish(processed)

    def prepare(self, input: str) -> str:
        return input.strip()

    @abstractmethod
    def process(self, input: str) -> str: ...

    def finish(self, input: str) -> str:
        return f"storage|{input}"

class StorageUpperTemplate(StorageTemplate):
    def process(self, input: str) -> str:
        return input.upper()
