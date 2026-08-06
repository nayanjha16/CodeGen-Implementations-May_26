"""DesignPatternsSolid | kind=design_pattern | label=state | domain=wallet | tier=minimal"""
from __future__ import annotations

from __future__ import annotations
from abc import ABC, abstractmethod

class WalletState(ABC):
    @abstractmethod
    def handle(self, ctx: "WalletContext") -> str: ...

class WalletOnState(WalletState):
    def handle(self, ctx: "WalletContext") -> str:
        ctx.set_state(WalletOffState())
        return "was-on-wallet"

class WalletOffState(WalletState):
    def handle(self, ctx: "WalletContext") -> str:
        ctx.set_state(WalletOnState())
        return "was-off-wallet"

class WalletContext:
    def __init__(self) -> None:
        self.state: WalletState = WalletOffState()

    def set_state(self, state: WalletState) -> None:
        self.state = state

    def request(self) -> str:
        return self.state.handle(self)
