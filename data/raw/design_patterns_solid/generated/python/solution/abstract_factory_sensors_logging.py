"""DesignPatternsSolid | kind=design_pattern | label=abstract factory | domain=sensors | tier=logging"""
from __future__ import annotations

from abc import ABC, abstractmethod

class SensorsButton(ABC):
    @abstractmethod
    def render(self) -> str: ...

class SensorsDialog(ABC):
    @abstractmethod
    def show(self) -> str: ...

class SensorsCloudButton(SensorsButton):
    def render(self) -> str: return "cloud-btn-sensors"

class SensorsCloudDialog(SensorsDialog):
    def show(self) -> str: return "cloud-dlg-sensors"

class SensorsLocalButton(SensorsButton):
    def render(self) -> str: return "local-btn-sensors"

class SensorsLocalDialog(SensorsDialog):
    def show(self) -> str: return "local-dlg-sensors"

class SensorsUIFactory(ABC):
    @abstractmethod
    def create_button(self) -> SensorsButton: ...
    @abstractmethod
    def create_dialog(self) -> SensorsDialog: ...

class SensorsCloudFactory(SensorsUIFactory):
    def create_button(self) -> SensorsButton: return SensorsCloudButton()
    def create_dialog(self) -> SensorsDialog: return SensorsCloudDialog()

class SensorsLocalFactory(SensorsUIFactory):
    def create_button(self) -> SensorsButton: return SensorsLocalButton()
    def create_dialog(self) -> SensorsDialog: return SensorsLocalDialog()

def run_ui(factory: SensorsUIFactory) -> str:
    return factory.create_button().render() + "|" + factory.create_dialog().show()
