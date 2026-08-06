"""DesignPatternsSolid | kind=design_pattern | label=factory | domain=wallet | tier=minimal"""
from __future__ import annotations

from abc import ABC, abstractmethod

class WalletProduct(ABC):
    @abstractmethod
    def operate(self) -> str:
        ...

class WalletBasicProduct(WalletProduct):
    def operate(self) -> str:
        return "basic-wallet"

class WalletPremiumProduct(WalletProduct):
    def operate(self) -> str:
        return "premium-wallet"

class WalletFactory:
    def create(self, type_name: str) -> WalletProduct:
        if type_name.lower() == "premium":
            return WalletPremiumProduct()
        return WalletBasicProduct()
