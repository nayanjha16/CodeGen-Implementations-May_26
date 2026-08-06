"""DesignPatternsSolid | kind=design_pattern | label=template method | domain=queue | tier=logging"""
from __future__ import annotations

from abc import ABC, abstractmethod

class QueueTemplate(ABC):
    def run(self, input: str) -> str:
        prepared = self.prepare(input)
        processed = self.process(prepared)
        return self.finish(processed)

    def prepare(self, input: str) -> str:
        return input.strip()

    @abstractmethod
    def process(self, input: str) -> str: ...

    def finish(self, input: str) -> str:
        return f"queue|{input}"

class QueueUpperTemplate(QueueTemplate):
    def process(self, input: str) -> str:
        return input.upper()
