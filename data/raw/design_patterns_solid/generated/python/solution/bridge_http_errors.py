"""DesignPatternsSolid | kind=design_pattern | label=bridge | domain=http | tier=errors"""
from __future__ import annotations

from abc import ABC, abstractmethod

class HttpImpl(ABC):
    @abstractmethod
    def write(self, msg: str) -> str: ...

class HttpFileImpl(HttpImpl):
    def write(self, msg: str) -> str:
        return f"file:http:{msg}"

class HttpMemoryImpl(HttpImpl):
    def write(self, msg: str) -> str:
        return f"mem:http:{msg}"

class HttpBridge(ABC):
    def __init__(self, impl: HttpImpl) -> None:
        self.impl = impl

    @abstractmethod
    def send(self, msg: str) -> str: ...

class HttpAlertBridge(HttpBridge):
    def send(self, msg: str) -> str:
        return self.impl.write("ALERT-" + msg)
