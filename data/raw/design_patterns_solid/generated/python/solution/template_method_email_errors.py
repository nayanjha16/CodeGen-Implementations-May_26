"""DesignPatternsSolid | kind=design_pattern | label=template method | domain=email | tier=errors"""
from __future__ import annotations

from abc import ABC, abstractmethod

class EmailTemplate(ABC):
    def run(self, input: str) -> str:
        prepared = self.prepare(input)
        processed = self.process(prepared)
        return self.finish(processed)

    def prepare(self, input: str) -> str:
        return input.strip()

    @abstractmethod
    def process(self, input: str) -> str: ...

    def finish(self, input: str) -> str:
        return f"email|{input}"

class EmailUpperTemplate(EmailTemplate):
    def process(self, input: str) -> str:
        return input.upper()
