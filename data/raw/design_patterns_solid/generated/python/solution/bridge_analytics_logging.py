"""DesignPatternsSolid | kind=design_pattern | label=bridge | domain=analytics | tier=logging"""
from __future__ import annotations

from abc import ABC, abstractmethod

class AnalyticsImpl(ABC):
    @abstractmethod
    def write(self, msg: str) -> str: ...

class AnalyticsFileImpl(AnalyticsImpl):
    def write(self, msg: str) -> str:
        return f"file:analytics:{msg}"

class AnalyticsMemoryImpl(AnalyticsImpl):
    def write(self, msg: str) -> str:
        return f"mem:analytics:{msg}"

class AnalyticsBridge(ABC):
    def __init__(self, impl: AnalyticsImpl) -> None:
        self.impl = impl

    @abstractmethod
    def send(self, msg: str) -> str: ...

class AnalyticsAlertBridge(AnalyticsBridge):
    def send(self, msg: str) -> str:
        return self.impl.write("ALERT-" + msg)
