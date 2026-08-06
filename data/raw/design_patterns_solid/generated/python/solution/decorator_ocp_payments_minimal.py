"""DesignPatternsSolid | kind=combo | label=decorator+ocp | domain=payments | tier=minimal"""
from __future__ import annotations

from abc import ABC, abstractmethod

class PaymentsComponent(ABC):
    @abstractmethod
    def process(self, input: str) -> str: ...

class PaymentsCore(PaymentsComponent):
    def process(self, input: str) -> str:
        return f"payments:{input}"

class PaymentsUpperDecorator(PaymentsComponent):
    def __init__(self, inner: PaymentsComponent) -> None:
        self.inner = inner

    def process(self, input: str) -> str:
        return self.inner.process(input).upper()
