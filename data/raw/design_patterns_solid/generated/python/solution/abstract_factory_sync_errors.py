"""DesignPatternsSolid | kind=design_pattern | label=abstract factory | domain=sync | tier=errors"""
from __future__ import annotations

from abc import ABC, abstractmethod

class SyncButton(ABC):
    @abstractmethod
    def render(self) -> str: ...

class SyncDialog(ABC):
    @abstractmethod
    def show(self) -> str: ...

class SyncCloudButton(SyncButton):
    def render(self) -> str: return "cloud-btn-sync"

class SyncCloudDialog(SyncDialog):
    def show(self) -> str: return "cloud-dlg-sync"

class SyncLocalButton(SyncButton):
    def render(self) -> str: return "local-btn-sync"

class SyncLocalDialog(SyncDialog):
    def show(self) -> str: return "local-dlg-sync"

class SyncUIFactory(ABC):
    @abstractmethod
    def create_button(self) -> SyncButton: ...
    @abstractmethod
    def create_dialog(self) -> SyncDialog: ...

class SyncCloudFactory(SyncUIFactory):
    def create_button(self) -> SyncButton: return SyncCloudButton()
    def create_dialog(self) -> SyncDialog: return SyncCloudDialog()

class SyncLocalFactory(SyncUIFactory):
    def create_button(self) -> SyncButton: return SyncLocalButton()
    def create_dialog(self) -> SyncDialog: return SyncLocalDialog()

def run_ui(factory: SyncUIFactory) -> str:
    return factory.create_button().render() + "|" + factory.create_dialog().show()
