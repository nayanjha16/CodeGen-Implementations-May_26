"""DesignPatternsSolid | kind=design_pattern | label=abstract factory | domain=widgets | tier=logging"""
from __future__ import annotations

from abc import ABC, abstractmethod

class WidgetsButton(ABC):
    @abstractmethod
    def render(self) -> str: ...

class WidgetsDialog(ABC):
    @abstractmethod
    def show(self) -> str: ...

class WidgetsCloudButton(WidgetsButton):
    def render(self) -> str: return "cloud-btn-widgets"

class WidgetsCloudDialog(WidgetsDialog):
    def show(self) -> str: return "cloud-dlg-widgets"

class WidgetsLocalButton(WidgetsButton):
    def render(self) -> str: return "local-btn-widgets"

class WidgetsLocalDialog(WidgetsDialog):
    def show(self) -> str: return "local-dlg-widgets"

class WidgetsUIFactory(ABC):
    @abstractmethod
    def create_button(self) -> WidgetsButton: ...
    @abstractmethod
    def create_dialog(self) -> WidgetsDialog: ...

class WidgetsCloudFactory(WidgetsUIFactory):
    def create_button(self) -> WidgetsButton: return WidgetsCloudButton()
    def create_dialog(self) -> WidgetsDialog: return WidgetsCloudDialog()

class WidgetsLocalFactory(WidgetsUIFactory):
    def create_button(self) -> WidgetsButton: return WidgetsLocalButton()
    def create_dialog(self) -> WidgetsDialog: return WidgetsLocalDialog()

def run_ui(factory: WidgetsUIFactory) -> str:
    return factory.create_button().render() + "|" + factory.create_dialog().show()
