"""DesignPatternsSolid | kind=design_pattern | label=abstract factory | domain=payments | tier=logging"""
from __future__ import annotations

from abc import ABC, abstractmethod

class PaymentsButton(ABC):
    @abstractmethod
    def render(self) -> str: ...

class PaymentsDialog(ABC):
    @abstractmethod
    def show(self) -> str: ...

class PaymentsCloudButton(PaymentsButton):
    def render(self) -> str: return "cloud-btn-payments"

class PaymentsCloudDialog(PaymentsDialog):
    def show(self) -> str: return "cloud-dlg-payments"

class PaymentsLocalButton(PaymentsButton):
    def render(self) -> str: return "local-btn-payments"

class PaymentsLocalDialog(PaymentsDialog):
    def show(self) -> str: return "local-dlg-payments"

class PaymentsUIFactory(ABC):
    @abstractmethod
    def create_button(self) -> PaymentsButton: ...
    @abstractmethod
    def create_dialog(self) -> PaymentsDialog: ...

class PaymentsCloudFactory(PaymentsUIFactory):
    def create_button(self) -> PaymentsButton: return PaymentsCloudButton()
    def create_dialog(self) -> PaymentsDialog: return PaymentsCloudDialog()

class PaymentsLocalFactory(PaymentsUIFactory):
    def create_button(self) -> PaymentsButton: return PaymentsLocalButton()
    def create_dialog(self) -> PaymentsDialog: return PaymentsLocalDialog()

def run_ui(factory: PaymentsUIFactory) -> str:
    return factory.create_button().render() + "|" + factory.create_dialog().show()
