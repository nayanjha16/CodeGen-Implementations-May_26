"""DesignPatternsSolid | kind=design_pattern | label=proxy | domain=sms | tier=logging"""
from __future__ import annotations

from abc import ABC, abstractmethod

class SmsService(ABC):
    @abstractmethod
    def load(self, id: str) -> str: ...

class SmsRealService(SmsService):
    def load(self, id: str) -> str:
        return f"real-sms:{id}"

class SmsProxy(SmsService):
    def __init__(self, allowed: bool) -> None:
        self.allowed = allowed
        self._real: SmsRealService | None = None

    def load(self, id: str) -> str:
        if not self.allowed:
            return "denied"
        if self._real is None:
            self._real = SmsRealService()
        return self._real.load(id)
