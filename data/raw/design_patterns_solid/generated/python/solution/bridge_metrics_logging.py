"""DesignPatternsSolid | kind=design_pattern | label=bridge | domain=metrics | tier=logging"""
from __future__ import annotations

from abc import ABC, abstractmethod

class MetricsImpl(ABC):
    @abstractmethod
    def write(self, msg: str) -> str: ...

class MetricsFileImpl(MetricsImpl):
    def write(self, msg: str) -> str:
        return f"file:metrics:{msg}"

class MetricsMemoryImpl(MetricsImpl):
    def write(self, msg: str) -> str:
        return f"mem:metrics:{msg}"

class MetricsBridge(ABC):
    def __init__(self, impl: MetricsImpl) -> None:
        self.impl = impl

    @abstractmethod
    def send(self, msg: str) -> str: ...

class MetricsAlertBridge(MetricsBridge):
    def send(self, msg: str) -> str:
        return self.impl.write("ALERT-" + msg)
