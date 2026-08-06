"""DesignPatternsSolid | kind=solid | label=dip | domain=sms | tier=minimal"""
from __future__ import annotations

from abc import ABC, abstractmethod

class SmsGateway(ABC):
    @abstractmethod
    def send(self, payload: str) -> str: ...

class SmsHttpGateway(SmsGateway):
    def send(self, payload: str) -> str:
        return f"http-sms:{payload}"

class SmsAppService:
    def __init__(self, gateway: SmsGateway) -> None:
        self.gateway = gateway

    def publish(self, payload: str) -> str:
        return self.gateway.send(payload)
