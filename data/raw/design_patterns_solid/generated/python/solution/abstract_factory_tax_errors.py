"""DesignPatternsSolid | kind=design_pattern | label=abstract factory | domain=tax | tier=errors"""
from __future__ import annotations

from abc import ABC, abstractmethod

class TaxButton(ABC):
    @abstractmethod
    def render(self) -> str: ...

class TaxDialog(ABC):
    @abstractmethod
    def show(self) -> str: ...

class TaxCloudButton(TaxButton):
    def render(self) -> str: return "cloud-btn-tax"

class TaxCloudDialog(TaxDialog):
    def show(self) -> str: return "cloud-dlg-tax"

class TaxLocalButton(TaxButton):
    def render(self) -> str: return "local-btn-tax"

class TaxLocalDialog(TaxDialog):
    def show(self) -> str: return "local-dlg-tax"

class TaxUIFactory(ABC):
    @abstractmethod
    def create_button(self) -> TaxButton: ...
    @abstractmethod
    def create_dialog(self) -> TaxDialog: ...

class TaxCloudFactory(TaxUIFactory):
    def create_button(self) -> TaxButton: return TaxCloudButton()
    def create_dialog(self) -> TaxDialog: return TaxCloudDialog()

class TaxLocalFactory(TaxUIFactory):
    def create_button(self) -> TaxButton: return TaxLocalButton()
    def create_dialog(self) -> TaxDialog: return TaxLocalDialog()

def run_ui(factory: TaxUIFactory) -> str:
    return factory.create_button().render() + "|" + factory.create_dialog().show()
