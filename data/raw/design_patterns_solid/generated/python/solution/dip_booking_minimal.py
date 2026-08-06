"""DesignPatternsSolid | kind=solid | label=dip | domain=booking | tier=minimal"""
from __future__ import annotations

from abc import ABC, abstractmethod

class BookingGateway(ABC):
    @abstractmethod
    def send(self, payload: str) -> str: ...

class BookingHttpGateway(BookingGateway):
    def send(self, payload: str) -> str:
        return f"http-booking:{payload}"

class BookingAppService:
    def __init__(self, gateway: BookingGateway) -> None:
        self.gateway = gateway

    def publish(self, payload: str) -> str:
        return self.gateway.send(payload)
