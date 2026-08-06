"""DesignPatternsSolid | kind=design_pattern | label=bridge | domain=email | tier=minimal"""
from __future__ import annotations

from abc import ABC, abstractmethod

class EmailImpl(ABC):
    @abstractmethod
    def write(self, msg: str) -> str: ...

class EmailFileImpl(EmailImpl):
    def write(self, msg: str) -> str:
        return f"file:email:{msg}"

class EmailMemoryImpl(EmailImpl):
    def write(self, msg: str) -> str:
        return f"mem:email:{msg}"

class EmailBridge(ABC):
    def __init__(self, impl: EmailImpl) -> None:
        self.impl = impl

    @abstractmethod
    def send(self, msg: str) -> str: ...

class EmailAlertBridge(EmailBridge):
    def send(self, msg: str) -> str:
        return self.impl.write("ALERT-" + msg)
