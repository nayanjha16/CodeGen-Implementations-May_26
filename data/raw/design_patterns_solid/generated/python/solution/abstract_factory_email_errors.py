"""DesignPatternsSolid | kind=design_pattern | label=abstract factory | domain=email | tier=errors"""
from __future__ import annotations

from abc import ABC, abstractmethod

class EmailButton(ABC):
    @abstractmethod
    def render(self) -> str: ...

class EmailDialog(ABC):
    @abstractmethod
    def show(self) -> str: ...

class EmailCloudButton(EmailButton):
    def render(self) -> str: return "cloud-btn-email"

class EmailCloudDialog(EmailDialog):
    def show(self) -> str: return "cloud-dlg-email"

class EmailLocalButton(EmailButton):
    def render(self) -> str: return "local-btn-email"

class EmailLocalDialog(EmailDialog):
    def show(self) -> str: return "local-dlg-email"

class EmailUIFactory(ABC):
    @abstractmethod
    def create_button(self) -> EmailButton: ...
    @abstractmethod
    def create_dialog(self) -> EmailDialog: ...

class EmailCloudFactory(EmailUIFactory):
    def create_button(self) -> EmailButton: return EmailCloudButton()
    def create_dialog(self) -> EmailDialog: return EmailCloudDialog()

class EmailLocalFactory(EmailUIFactory):
    def create_button(self) -> EmailButton: return EmailLocalButton()
    def create_dialog(self) -> EmailDialog: return EmailLocalDialog()

def run_ui(factory: EmailUIFactory) -> str:
    return factory.create_button().render() + "|" + factory.create_dialog().show()
