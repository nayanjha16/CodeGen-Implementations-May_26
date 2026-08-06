"""DesignPatternsSolid | kind=design_pattern | label=decorator | domain=wallet | tier=minimal"""
from __future__ import annotations

from abc import ABC, abstractmethod

class WalletComponent(ABC):
    @abstractmethod
    def process(self, input: str) -> str: ...

class WalletCore(WalletComponent):
    def process(self, input: str) -> str:
        return f"wallet:{input}"

class WalletUpperDecorator(WalletComponent):
    def __init__(self, inner: WalletComponent) -> None:
        self.inner = inner

    def process(self, input: str) -> str:
        return self.inner.process(input).upper()
