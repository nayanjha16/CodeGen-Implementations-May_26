"""DesignPatternsSolid | kind=design_pattern | label=abstract factory | domain=plugin | tier=errors"""
from __future__ import annotations

from abc import ABC, abstractmethod

class PluginButton(ABC):
    @abstractmethod
    def render(self) -> str: ...

class PluginDialog(ABC):
    @abstractmethod
    def show(self) -> str: ...

class PluginCloudButton(PluginButton):
    def render(self) -> str: return "cloud-btn-plugin"

class PluginCloudDialog(PluginDialog):
    def show(self) -> str: return "cloud-dlg-plugin"

class PluginLocalButton(PluginButton):
    def render(self) -> str: return "local-btn-plugin"

class PluginLocalDialog(PluginDialog):
    def show(self) -> str: return "local-dlg-plugin"

class PluginUIFactory(ABC):
    @abstractmethod
    def create_button(self) -> PluginButton: ...
    @abstractmethod
    def create_dialog(self) -> PluginDialog: ...

class PluginCloudFactory(PluginUIFactory):
    def create_button(self) -> PluginButton: return PluginCloudButton()
    def create_dialog(self) -> PluginDialog: return PluginCloudDialog()

class PluginLocalFactory(PluginUIFactory):
    def create_button(self) -> PluginButton: return PluginLocalButton()
    def create_dialog(self) -> PluginDialog: return PluginLocalDialog()

def run_ui(factory: PluginUIFactory) -> str:
    return factory.create_button().render() + "|" + factory.create_dialog().show()
