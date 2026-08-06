"""DesignPatternsSolid | kind=design_pattern | label=abstract factory | domain=storage | tier=errors"""
from __future__ import annotations

from abc import ABC, abstractmethod

class StorageButton(ABC):
    @abstractmethod
    def render(self) -> str: ...

class StorageDialog(ABC):
    @abstractmethod
    def show(self) -> str: ...

class StorageCloudButton(StorageButton):
    def render(self) -> str: return "cloud-btn-storage"

class StorageCloudDialog(StorageDialog):
    def show(self) -> str: return "cloud-dlg-storage"

class StorageLocalButton(StorageButton):
    def render(self) -> str: return "local-btn-storage"

class StorageLocalDialog(StorageDialog):
    def show(self) -> str: return "local-dlg-storage"

class StorageUIFactory(ABC):
    @abstractmethod
    def create_button(self) -> StorageButton: ...
    @abstractmethod
    def create_dialog(self) -> StorageDialog: ...

class StorageCloudFactory(StorageUIFactory):
    def create_button(self) -> StorageButton: return StorageCloudButton()
    def create_dialog(self) -> StorageDialog: return StorageCloudDialog()

class StorageLocalFactory(StorageUIFactory):
    def create_button(self) -> StorageButton: return StorageLocalButton()
    def create_dialog(self) -> StorageDialog: return StorageLocalDialog()

def run_ui(factory: StorageUIFactory) -> str:
    return factory.create_button().render() + "|" + factory.create_dialog().show()
