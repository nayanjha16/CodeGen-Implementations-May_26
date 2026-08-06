"""DesignPatternsSolid | kind=design_pattern | label=template method | domain=cart | tier=minimal"""
from __future__ import annotations

from abc import ABC, abstractmethod

class CartTemplate(ABC):
    def run(self, input: str) -> str:
        prepared = self.prepare(input)
        processed = self.process(prepared)
        return self.finish(processed)

    def prepare(self, input: str) -> str:
        return input.strip()

    @abstractmethod
    def process(self, input: str) -> str: ...

    def finish(self, input: str) -> str:
        return f"cart|{input}"

class CartUpperTemplate(CartTemplate):
    def process(self, input: str) -> str:
        return input.upper()
