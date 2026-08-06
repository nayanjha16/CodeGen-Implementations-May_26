"""DesignPatternsSolid | kind=design_pattern | label=abstract factory | domain=http | tier=logging"""
from __future__ import annotations

from abc import ABC, abstractmethod

class HttpButton(ABC):
    @abstractmethod
    def render(self) -> str: ...

class HttpDialog(ABC):
    @abstractmethod
    def show(self) -> str: ...

class HttpCloudButton(HttpButton):
    def render(self) -> str: return "cloud-btn-http"

class HttpCloudDialog(HttpDialog):
    def show(self) -> str: return "cloud-dlg-http"

class HttpLocalButton(HttpButton):
    def render(self) -> str: return "local-btn-http"

class HttpLocalDialog(HttpDialog):
    def show(self) -> str: return "local-dlg-http"

class HttpUIFactory(ABC):
    @abstractmethod
    def create_button(self) -> HttpButton: ...
    @abstractmethod
    def create_dialog(self) -> HttpDialog: ...

class HttpCloudFactory(HttpUIFactory):
    def create_button(self) -> HttpButton: return HttpCloudButton()
    def create_dialog(self) -> HttpDialog: return HttpCloudDialog()

class HttpLocalFactory(HttpUIFactory):
    def create_button(self) -> HttpButton: return HttpLocalButton()
    def create_dialog(self) -> HttpDialog: return HttpLocalDialog()

def run_ui(factory: HttpUIFactory) -> str:
    return factory.create_button().render() + "|" + factory.create_dialog().show()
