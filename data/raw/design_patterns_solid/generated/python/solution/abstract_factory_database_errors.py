"""DesignPatternsSolid | kind=design_pattern | label=abstract factory | domain=database | tier=errors"""
from __future__ import annotations

from abc import ABC, abstractmethod

class DatabaseButton(ABC):
    @abstractmethod
    def render(self) -> str: ...

class DatabaseDialog(ABC):
    @abstractmethod
    def show(self) -> str: ...

class DatabaseCloudButton(DatabaseButton):
    def render(self) -> str: return "cloud-btn-database"

class DatabaseCloudDialog(DatabaseDialog):
    def show(self) -> str: return "cloud-dlg-database"

class DatabaseLocalButton(DatabaseButton):
    def render(self) -> str: return "local-btn-database"

class DatabaseLocalDialog(DatabaseDialog):
    def show(self) -> str: return "local-dlg-database"

class DatabaseUIFactory(ABC):
    @abstractmethod
    def create_button(self) -> DatabaseButton: ...
    @abstractmethod
    def create_dialog(self) -> DatabaseDialog: ...

class DatabaseCloudFactory(DatabaseUIFactory):
    def create_button(self) -> DatabaseButton: return DatabaseCloudButton()
    def create_dialog(self) -> DatabaseDialog: return DatabaseCloudDialog()

class DatabaseLocalFactory(DatabaseUIFactory):
    def create_button(self) -> DatabaseButton: return DatabaseLocalButton()
    def create_dialog(self) -> DatabaseDialog: return DatabaseLocalDialog()

def run_ui(factory: DatabaseUIFactory) -> str:
    return factory.create_button().render() + "|" + factory.create_dialog().show()
