"""DesignPatternsSolid | kind=combo | label=decorator+ocp | domain=billing | tier=minimal"""
from __future__ import annotations

from abc import ABC, abstractmethod

class BillingComponent(ABC):
    @abstractmethod
    def process(self, input: str) -> str: ...

class BillingCore(BillingComponent):
    def process(self, input: str) -> str:
        return f"billing:{input}"

class BillingUpperDecorator(BillingComponent):
    def __init__(self, inner: BillingComponent) -> None:
        self.inner = inner

    def process(self, input: str) -> str:
        return self.inner.process(input).upper()
