"""DesignPatternsSolid | kind=design_pattern | label=template method | domain=payments | tier=logging"""
from __future__ import annotations

from abc import ABC, abstractmethod

class PaymentsTemplate(ABC):
    def run(self, input: str) -> str:
        prepared = self.prepare(input)
        processed = self.process(prepared)
        return self.finish(processed)

    def prepare(self, input: str) -> str:
        return input.strip()

    @abstractmethod
    def process(self, input: str) -> str: ...

    def finish(self, input: str) -> str:
        return f"payments|{input}"

class PaymentsUpperTemplate(PaymentsTemplate):
    def process(self, input: str) -> str:
        return input.upper()
