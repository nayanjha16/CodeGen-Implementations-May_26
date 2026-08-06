"""DesignPatternsSolid | kind=design_pattern | label=bridge | domain=cache | tier=minimal"""
from __future__ import annotations

from abc import ABC, abstractmethod

class CacheImpl(ABC):
    @abstractmethod
    def write(self, msg: str) -> str: ...

class CacheFileImpl(CacheImpl):
    def write(self, msg: str) -> str:
        return f"file:cache:{msg}"

class CacheMemoryImpl(CacheImpl):
    def write(self, msg: str) -> str:
        return f"mem:cache:{msg}"

class CacheBridge(ABC):
    def __init__(self, impl: CacheImpl) -> None:
        self.impl = impl

    @abstractmethod
    def send(self, msg: str) -> str: ...

class CacheAlertBridge(CacheBridge):
    def send(self, msg: str) -> str:
        return self.impl.write("ALERT-" + msg)
