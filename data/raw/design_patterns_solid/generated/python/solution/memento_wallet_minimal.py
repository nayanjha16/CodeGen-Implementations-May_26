"""DesignPatternsSolid | kind=design_pattern | label=memento | domain=wallet | tier=minimal"""
from __future__ import annotations

from dataclasses import dataclass

@dataclass(frozen=True)
class WalletMemento:
    state: str

class WalletOriginator:
    def __init__(self) -> None:
        self.state = "wallet-init"

    def set_state(self, state: str) -> None:
        self.state = state

    def get_state(self) -> str:
        return self.state

    def save(self) -> WalletMemento:
        return WalletMemento(self.state)

    def restore(self, m: WalletMemento) -> None:
        self.state = m.state
