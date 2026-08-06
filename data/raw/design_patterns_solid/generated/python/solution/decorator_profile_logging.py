"""DesignPatternsSolid | kind=design_pattern | label=decorator | domain=profile | tier=logging"""
from __future__ import annotations

from abc import ABC, abstractmethod

class ProfileComponent(ABC):
    @abstractmethod
    def process(self, input: str) -> str: ...

class ProfileCore(ProfileComponent):
    def process(self, input: str) -> str:
        return f"profile:{input}"

class ProfileUpperDecorator(ProfileComponent):
    def __init__(self, inner: ProfileComponent) -> None:
        self.inner = inner

    def process(self, input: str) -> str:
        return self.inner.process(input).upper()
