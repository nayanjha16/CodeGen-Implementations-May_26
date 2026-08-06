"""DesignPatternsSolid | kind=design_pattern | label=bridge | domain=search | tier=errors"""
from __future__ import annotations

from abc import ABC, abstractmethod

class SearchImpl(ABC):
    @abstractmethod
    def write(self, msg: str) -> str: ...

class SearchFileImpl(SearchImpl):
    def write(self, msg: str) -> str:
        return f"file:search:{msg}"

class SearchMemoryImpl(SearchImpl):
    def write(self, msg: str) -> str:
        return f"mem:search:{msg}"

class SearchBridge(ABC):
    def __init__(self, impl: SearchImpl) -> None:
        self.impl = impl

    @abstractmethod
    def send(self, msg: str) -> str: ...

class SearchAlertBridge(SearchBridge):
    def send(self, msg: str) -> str:
        return self.impl.write("ALERT-" + msg)
