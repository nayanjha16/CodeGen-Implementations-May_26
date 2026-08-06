"""DesignPatternsSolid | kind=design_pattern | label=decorator | domain=sms | tier=minimal"""
from __future__ import annotations

from abc import ABC, abstractmethod

class SmsComponent(ABC):
    @abstractmethod
    def process(self, input: str) -> str: ...

class SmsCore(SmsComponent):
    def process(self, input: str) -> str:
        return f"sms:{input}"

class SmsUpperDecorator(SmsComponent):
    def __init__(self, inner: SmsComponent) -> None:
        self.inner = inner

    def process(self, input: str) -> str:
        return self.inner.process(input).upper()
