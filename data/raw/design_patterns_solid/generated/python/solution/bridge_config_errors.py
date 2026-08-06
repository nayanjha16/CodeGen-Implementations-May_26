"""DesignPatternsSolid | kind=design_pattern | label=bridge | domain=config | tier=errors"""
from __future__ import annotations

from abc import ABC, abstractmethod

class ConfigImpl(ABC):
    @abstractmethod
    def write(self, msg: str) -> str: ...

class ConfigFileImpl(ConfigImpl):
    def write(self, msg: str) -> str:
        return f"file:config:{msg}"

class ConfigMemoryImpl(ConfigImpl):
    def write(self, msg: str) -> str:
        return f"mem:config:{msg}"

class ConfigBridge(ABC):
    def __init__(self, impl: ConfigImpl) -> None:
        self.impl = impl

    @abstractmethod
    def send(self, msg: str) -> str: ...

class ConfigAlertBridge(ConfigBridge):
    def send(self, msg: str) -> str:
        return self.impl.write("ALERT-" + msg)
