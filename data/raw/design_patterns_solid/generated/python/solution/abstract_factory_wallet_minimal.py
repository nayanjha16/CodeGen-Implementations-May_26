"""DesignPatternsSolid | kind=design_pattern | label=abstract factory | domain=wallet | tier=minimal"""
from __future__ import annotations

from abc import ABC, abstractmethod

class WalletButton(ABC):
    @abstractmethod
    def render(self) -> str: ...

class WalletDialog(ABC):
    @abstractmethod
    def show(self) -> str: ...

class WalletCloudButton(WalletButton):
    def render(self) -> str: return "cloud-btn-wallet"

class WalletCloudDialog(WalletDialog):
    def show(self) -> str: return "cloud-dlg-wallet"

class WalletLocalButton(WalletButton):
    def render(self) -> str: return "local-btn-wallet"

class WalletLocalDialog(WalletDialog):
    def show(self) -> str: return "local-dlg-wallet"

class WalletUIFactory(ABC):
    @abstractmethod
    def create_button(self) -> WalletButton: ...
    @abstractmethod
    def create_dialog(self) -> WalletDialog: ...

class WalletCloudFactory(WalletUIFactory):
    def create_button(self) -> WalletButton: return WalletCloudButton()
    def create_dialog(self) -> WalletDialog: return WalletCloudDialog()

class WalletLocalFactory(WalletUIFactory):
    def create_button(self) -> WalletButton: return WalletLocalButton()
    def create_dialog(self) -> WalletDialog: return WalletLocalDialog()

def run_ui(factory: WalletUIFactory) -> str:
    return factory.create_button().render() + "|" + factory.create_dialog().show()
