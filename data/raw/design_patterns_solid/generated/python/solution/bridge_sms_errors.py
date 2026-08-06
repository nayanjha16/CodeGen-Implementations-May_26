"""DesignPatternsSolid | kind=design_pattern | label=bridge | domain=sms | tier=errors"""
from __future__ import annotations

from abc import ABC, abstractmethod

class SmsImpl(ABC):
    @abstractmethod
    def write(self, msg: str) -> str: ...

class SmsFileImpl(SmsImpl):
    def write(self, msg: str) -> str:
        return f"file:sms:{msg}"

class SmsMemoryImpl(SmsImpl):
    def write(self, msg: str) -> str:
        return f"mem:sms:{msg}"

class SmsBridge(ABC):
    def __init__(self, impl: SmsImpl) -> None:
        self.impl = impl

    @abstractmethod
    def send(self, msg: str) -> str: ...

class SmsAlertBridge(SmsBridge):
    def send(self, msg: str) -> str:
        return self.impl.write("ALERT-" + msg)
