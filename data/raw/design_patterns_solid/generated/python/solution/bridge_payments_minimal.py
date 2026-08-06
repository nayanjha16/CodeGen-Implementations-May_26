"""DesignPatternsSolid | kind=design_pattern | label=bridge | domain=payments | tier=minimal"""
from __future__ import annotations

from abc import ABC, abstractmethod

class PaymentsImpl(ABC):
    @abstractmethod
    def write(self, msg: str) -> str: ...

class PaymentsFileImpl(PaymentsImpl):
    def write(self, msg: str) -> str:
        return f"file:payments:{msg}"

class PaymentsMemoryImpl(PaymentsImpl):
    def write(self, msg: str) -> str:
        return f"mem:payments:{msg}"

class PaymentsBridge(ABC):
    def __init__(self, impl: PaymentsImpl) -> None:
        self.impl = impl

    @abstractmethod
    def send(self, msg: str) -> str: ...

class PaymentsAlertBridge(PaymentsBridge):
    def send(self, msg: str) -> str:
        return self.impl.write("ALERT-" + msg)
