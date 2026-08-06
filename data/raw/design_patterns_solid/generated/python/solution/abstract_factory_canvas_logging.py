"""DesignPatternsSolid | kind=design_pattern | label=abstract factory | domain=canvas | tier=logging"""
from __future__ import annotations

from abc import ABC, abstractmethod

class CanvasButton(ABC):
    @abstractmethod
    def render(self) -> str: ...

class CanvasDialog(ABC):
    @abstractmethod
    def show(self) -> str: ...

class CanvasCloudButton(CanvasButton):
    def render(self) -> str: return "cloud-btn-canvas"

class CanvasCloudDialog(CanvasDialog):
    def show(self) -> str: return "cloud-dlg-canvas"

class CanvasLocalButton(CanvasButton):
    def render(self) -> str: return "local-btn-canvas"

class CanvasLocalDialog(CanvasDialog):
    def show(self) -> str: return "local-dlg-canvas"

class CanvasUIFactory(ABC):
    @abstractmethod
    def create_button(self) -> CanvasButton: ...
    @abstractmethod
    def create_dialog(self) -> CanvasDialog: ...

class CanvasCloudFactory(CanvasUIFactory):
    def create_button(self) -> CanvasButton: return CanvasCloudButton()
    def create_dialog(self) -> CanvasDialog: return CanvasCloudDialog()

class CanvasLocalFactory(CanvasUIFactory):
    def create_button(self) -> CanvasButton: return CanvasLocalButton()
    def create_dialog(self) -> CanvasDialog: return CanvasLocalDialog()

def run_ui(factory: CanvasUIFactory) -> str:
    return factory.create_button().render() + "|" + factory.create_dialog().show()
