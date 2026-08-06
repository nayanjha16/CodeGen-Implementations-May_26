"""DesignPatternsSolid | kind=design_pattern | label=decorator | domain=license | tier=minimal"""
from __future__ import annotations

from abc import ABC, abstractmethod

class LicenseComponent(ABC):
    @abstractmethod
    def process(self, input: str) -> str: ...

class LicenseCore(LicenseComponent):
    def process(self, input: str) -> str:
        return f"license:{input}"

class LicenseUpperDecorator(LicenseComponent):
    def __init__(self, inner: LicenseComponent) -> None:
        self.inner = inner

    def process(self, input: str) -> str:
        return self.inner.process(input).upper()
