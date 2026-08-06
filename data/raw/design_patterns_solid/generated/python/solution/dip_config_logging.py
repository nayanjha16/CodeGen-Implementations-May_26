"""DesignPatternsSolid | kind=solid | label=dip | domain=config | tier=logging"""
from __future__ import annotations

from abc import ABC, abstractmethod

class ConfigGateway(ABC):
    @abstractmethod
    def send(self, payload: str) -> str: ...

class ConfigHttpGateway(ConfigGateway):
    def send(self, payload: str) -> str:
        return f"http-config:{payload}"

class ConfigAppService:
    def __init__(self, gateway: ConfigGateway) -> None:
        self.gateway = gateway

    def publish(self, payload: str) -> str:
        return self.gateway.send(payload)
