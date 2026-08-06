"""DesignPatternsSolid | kind=solid | label=dip | domain=review | tier=minimal"""
from __future__ import annotations

from abc import ABC, abstractmethod

class ReviewGateway(ABC):
    @abstractmethod
    def send(self, payload: str) -> str: ...

class ReviewHttpGateway(ReviewGateway):
    def send(self, payload: str) -> str:
        return f"http-review:{payload}"

class ReviewAppService:
    def __init__(self, gateway: ReviewGateway) -> None:
        self.gateway = gateway

    def publish(self, payload: str) -> str:
        return self.gateway.send(payload)
