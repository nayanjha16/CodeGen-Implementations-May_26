"""DesignPatternsSolid | kind=design_pattern | label=abstract factory | domain=discount | tier=logging"""
from __future__ import annotations

from abc import ABC, abstractmethod

class DiscountButton(ABC):
    @abstractmethod
    def render(self) -> str: ...

class DiscountDialog(ABC):
    @abstractmethod
    def show(self) -> str: ...

class DiscountCloudButton(DiscountButton):
    def render(self) -> str: return "cloud-btn-discount"

class DiscountCloudDialog(DiscountDialog):
    def show(self) -> str: return "cloud-dlg-discount"

class DiscountLocalButton(DiscountButton):
    def render(self) -> str: return "local-btn-discount"

class DiscountLocalDialog(DiscountDialog):
    def show(self) -> str: return "local-dlg-discount"

class DiscountUIFactory(ABC):
    @abstractmethod
    def create_button(self) -> DiscountButton: ...
    @abstractmethod
    def create_dialog(self) -> DiscountDialog: ...

class DiscountCloudFactory(DiscountUIFactory):
    def create_button(self) -> DiscountButton: return DiscountCloudButton()
    def create_dialog(self) -> DiscountDialog: return DiscountCloudDialog()

class DiscountLocalFactory(DiscountUIFactory):
    def create_button(self) -> DiscountButton: return DiscountLocalButton()
    def create_dialog(self) -> DiscountDialog: return DiscountLocalDialog()

def run_ui(factory: DiscountUIFactory) -> str:
    return factory.create_button().render() + "|" + factory.create_dialog().show()
