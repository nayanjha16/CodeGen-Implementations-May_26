"""DesignPatternsSolid | kind=design_pattern | label=bridge | domain=auth | tier=errors"""
from __future__ import annotations

from abc import ABC, abstractmethod

class AuthImpl(ABC):
    @abstractmethod
    def write(self, msg: str) -> str: ...

class AuthFileImpl(AuthImpl):
    def write(self, msg: str) -> str:
        return f"file:auth:{msg}"

class AuthMemoryImpl(AuthImpl):
    def write(self, msg: str) -> str:
        return f"mem:auth:{msg}"

class AuthBridge(ABC):
    def __init__(self, impl: AuthImpl) -> None:
        self.impl = impl

    @abstractmethod
    def send(self, msg: str) -> str: ...

class AuthAlertBridge(AuthBridge):
    def send(self, msg: str) -> str:
        return self.impl.write("ALERT-" + msg)
