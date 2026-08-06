"""DesignPatternsSolid | kind=combo | label=decorator+ocp | domain=report | tier=logging"""
from __future__ import annotations

from abc import ABC, abstractmethod

class ReportComponent(ABC):
    @abstractmethod
    def process(self, input: str) -> str: ...

class ReportCore(ReportComponent):
    def process(self, input: str) -> str:
        return f"report:{input}"

class ReportUpperDecorator(ReportComponent):
    def __init__(self, inner: ReportComponent) -> None:
        self.inner = inner

    def process(self, input: str) -> str:
        return self.inner.process(input).upper()
