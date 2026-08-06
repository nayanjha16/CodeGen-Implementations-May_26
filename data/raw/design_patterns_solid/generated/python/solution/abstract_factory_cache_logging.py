"""DesignPatternsSolid | kind=design_pattern | label=abstract factory | domain=cache | tier=logging"""
from __future__ import annotations

from abc import ABC, abstractmethod

class CacheButton(ABC):
    @abstractmethod
    def render(self) -> str: ...

class CacheDialog(ABC):
    @abstractmethod
    def show(self) -> str: ...

class CacheCloudButton(CacheButton):
    def render(self) -> str: return "cloud-btn-cache"

class CacheCloudDialog(CacheDialog):
    def show(self) -> str: return "cloud-dlg-cache"

class CacheLocalButton(CacheButton):
    def render(self) -> str: return "local-btn-cache"

class CacheLocalDialog(CacheDialog):
    def show(self) -> str: return "local-dlg-cache"

class CacheUIFactory(ABC):
    @abstractmethod
    def create_button(self) -> CacheButton: ...
    @abstractmethod
    def create_dialog(self) -> CacheDialog: ...

class CacheCloudFactory(CacheUIFactory):
    def create_button(self) -> CacheButton: return CacheCloudButton()
    def create_dialog(self) -> CacheDialog: return CacheCloudDialog()

class CacheLocalFactory(CacheUIFactory):
    def create_button(self) -> CacheButton: return CacheLocalButton()
    def create_dialog(self) -> CacheDialog: return CacheLocalDialog()

def run_ui(factory: CacheUIFactory) -> str:
    return factory.create_button().render() + "|" + factory.create_dialog().show()
