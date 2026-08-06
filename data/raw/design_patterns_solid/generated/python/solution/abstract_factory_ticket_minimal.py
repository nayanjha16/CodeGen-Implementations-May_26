"""DesignPatternsSolid | kind=design_pattern | label=abstract factory | domain=ticket | tier=minimal"""
from __future__ import annotations

from abc import ABC, abstractmethod

class TicketButton(ABC):
    @abstractmethod
    def render(self) -> str: ...

class TicketDialog(ABC):
    @abstractmethod
    def show(self) -> str: ...

class TicketCloudButton(TicketButton):
    def render(self) -> str: return "cloud-btn-ticket"

class TicketCloudDialog(TicketDialog):
    def show(self) -> str: return "cloud-dlg-ticket"

class TicketLocalButton(TicketButton):
    def render(self) -> str: return "local-btn-ticket"

class TicketLocalDialog(TicketDialog):
    def show(self) -> str: return "local-dlg-ticket"

class TicketUIFactory(ABC):
    @abstractmethod
    def create_button(self) -> TicketButton: ...
    @abstractmethod
    def create_dialog(self) -> TicketDialog: ...

class TicketCloudFactory(TicketUIFactory):
    def create_button(self) -> TicketButton: return TicketCloudButton()
    def create_dialog(self) -> TicketDialog: return TicketCloudDialog()

class TicketLocalFactory(TicketUIFactory):
    def create_button(self) -> TicketButton: return TicketLocalButton()
    def create_dialog(self) -> TicketDialog: return TicketLocalDialog()

def run_ui(factory: TicketUIFactory) -> str:
    return factory.create_button().render() + "|" + factory.create_dialog().show()
