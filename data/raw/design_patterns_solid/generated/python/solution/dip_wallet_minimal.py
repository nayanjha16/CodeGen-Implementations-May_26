"""DesignPatternsSolid | kind=solid | label=dip | domain=wallet | tier=minimal"""
from __future__ import annotations

from abc import ABC, abstractmethod

class WalletGateway(ABC):
    @abstractmethod
    def send(self, payload: str) -> str: ...

class WalletHttpGateway(WalletGateway):
    def send(self, payload: str) -> str:
        return f"http-wallet:{payload}"

class WalletAppService:
    def __init__(self, gateway: WalletGateway) -> None:
        self.gateway = gateway

    def publish(self, payload: str) -> str:
        return self.gateway.send(payload)
