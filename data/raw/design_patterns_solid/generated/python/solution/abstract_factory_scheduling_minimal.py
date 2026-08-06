"""DesignPatternsSolid | kind=design_pattern | label=abstract factory | domain=scheduling | tier=minimal"""
from __future__ import annotations

from abc import ABC, abstractmethod

class SchedulingButton(ABC):
    @abstractmethod
    def render(self) -> str: ...

class SchedulingDialog(ABC):
    @abstractmethod
    def show(self) -> str: ...

class SchedulingCloudButton(SchedulingButton):
    def render(self) -> str: return "cloud-btn-scheduling"

class SchedulingCloudDialog(SchedulingDialog):
    def show(self) -> str: return "cloud-dlg-scheduling"

class SchedulingLocalButton(SchedulingButton):
    def render(self) -> str: return "local-btn-scheduling"

class SchedulingLocalDialog(SchedulingDialog):
    def show(self) -> str: return "local-dlg-scheduling"

class SchedulingUIFactory(ABC):
    @abstractmethod
    def create_button(self) -> SchedulingButton: ...
    @abstractmethod
    def create_dialog(self) -> SchedulingDialog: ...

class SchedulingCloudFactory(SchedulingUIFactory):
    def create_button(self) -> SchedulingButton: return SchedulingCloudButton()
    def create_dialog(self) -> SchedulingDialog: return SchedulingCloudDialog()

class SchedulingLocalFactory(SchedulingUIFactory):
    def create_button(self) -> SchedulingButton: return SchedulingLocalButton()
    def create_dialog(self) -> SchedulingDialog: return SchedulingLocalDialog()

def run_ui(factory: SchedulingUIFactory) -> str:
    return factory.create_button().render() + "|" + factory.create_dialog().show()
