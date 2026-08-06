"""DesignPatternsSolid | kind=design_pattern | label=bridge | domain=todo | tier=minimal"""
from __future__ import annotations

from abc import ABC, abstractmethod

class TodoImpl(ABC):
    @abstractmethod
    def write(self, msg: str) -> str: ...

class TodoFileImpl(TodoImpl):
    def write(self, msg: str) -> str:
        return f"file:todo:{msg}"

class TodoMemoryImpl(TodoImpl):
    def write(self, msg: str) -> str:
        return f"mem:todo:{msg}"

class TodoBridge(ABC):
    def __init__(self, impl: TodoImpl) -> None:
        self.impl = impl

    @abstractmethod
    def send(self, msg: str) -> str: ...

class TodoAlertBridge(TodoBridge):
    def send(self, msg: str) -> str:
        return self.impl.write("ALERT-" + msg)
