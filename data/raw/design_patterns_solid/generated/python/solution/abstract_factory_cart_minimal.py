"""DesignPatternsSolid | kind=design_pattern | label=abstract factory | domain=cart | tier=minimal"""
from __future__ import annotations

from abc import ABC, abstractmethod

class CartButton(ABC):
    @abstractmethod
    def render(self) -> str: ...

class CartDialog(ABC):
    @abstractmethod
    def show(self) -> str: ...

class CartCloudButton(CartButton):
    def render(self) -> str: return "cloud-btn-cart"

class CartCloudDialog(CartDialog):
    def show(self) -> str: return "cloud-dlg-cart"

class CartLocalButton(CartButton):
    def render(self) -> str: return "local-btn-cart"

class CartLocalDialog(CartDialog):
    def show(self) -> str: return "local-dlg-cart"

class CartUIFactory(ABC):
    @abstractmethod
    def create_button(self) -> CartButton: ...
    @abstractmethod
    def create_dialog(self) -> CartDialog: ...

class CartCloudFactory(CartUIFactory):
    def create_button(self) -> CartButton: return CartCloudButton()
    def create_dialog(self) -> CartDialog: return CartCloudDialog()

class CartLocalFactory(CartUIFactory):
    def create_button(self) -> CartButton: return CartLocalButton()
    def create_dialog(self) -> CartDialog: return CartLocalDialog()

def run_ui(factory: CartUIFactory) -> str:
    return factory.create_button().render() + "|" + factory.create_dialog().show()
