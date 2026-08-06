"""DesignPatternsSolid | kind=design_pattern | label=abstract factory | domain=backup | tier=minimal"""
from __future__ import annotations

from abc import ABC, abstractmethod

class BackupButton(ABC):
    @abstractmethod
    def render(self) -> str: ...

class BackupDialog(ABC):
    @abstractmethod
    def show(self) -> str: ...

class BackupCloudButton(BackupButton):
    def render(self) -> str: return "cloud-btn-backup"

class BackupCloudDialog(BackupDialog):
    def show(self) -> str: return "cloud-dlg-backup"

class BackupLocalButton(BackupButton):
    def render(self) -> str: return "local-btn-backup"

class BackupLocalDialog(BackupDialog):
    def show(self) -> str: return "local-dlg-backup"

class BackupUIFactory(ABC):
    @abstractmethod
    def create_button(self) -> BackupButton: ...
    @abstractmethod
    def create_dialog(self) -> BackupDialog: ...

class BackupCloudFactory(BackupUIFactory):
    def create_button(self) -> BackupButton: return BackupCloudButton()
    def create_dialog(self) -> BackupDialog: return BackupCloudDialog()

class BackupLocalFactory(BackupUIFactory):
    def create_button(self) -> BackupButton: return BackupLocalButton()
    def create_dialog(self) -> BackupDialog: return BackupLocalDialog()

def run_ui(factory: BackupUIFactory) -> str:
    return factory.create_button().render() + "|" + factory.create_dialog().show()
