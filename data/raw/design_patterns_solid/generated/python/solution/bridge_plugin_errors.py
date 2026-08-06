"""DesignPatternsSolid | kind=design_pattern | label=bridge | domain=plugin | tier=errors"""
from __future__ import annotations

from abc import ABC, abstractmethod

class PluginImpl(ABC):
    @abstractmethod
    def write(self, msg: str) -> str: ...

class PluginFileImpl(PluginImpl):
    def write(self, msg: str) -> str:
        return f"file:plugin:{msg}"

class PluginMemoryImpl(PluginImpl):
    def write(self, msg: str) -> str:
        return f"mem:plugin:{msg}"

class PluginBridge(ABC):
    def __init__(self, impl: PluginImpl) -> None:
        self.impl = impl

    @abstractmethod
    def send(self, msg: str) -> str: ...

class PluginAlertBridge(PluginBridge):
    def send(self, msg: str) -> str:
        return self.impl.write("ALERT-" + msg)
