"""DesignPatternsSolid | kind=design_pattern | label=command | domain=wallet | tier=minimal"""
from __future__ import annotations

from abc import ABC, abstractmethod

class WalletCommand(ABC):
    @abstractmethod
    def execute(self) -> str: ...

class WalletReceiver:
    def action(self, x: str) -> str:
        return f"done-wallet:{x}"

class WalletActionCommand(WalletCommand):
    def __init__(self, receiver: WalletReceiver, payload: str) -> None:
        self.receiver = receiver
        self.payload = payload

    def execute(self) -> str:
        return self.receiver.action(self.payload)
