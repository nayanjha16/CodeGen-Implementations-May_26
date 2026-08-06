"""DesignPatternsSolid | kind=design_pattern | label=abstract factory | domain=session | tier=logging"""
from __future__ import annotations

from abc import ABC, abstractmethod

class SessionButton(ABC):
    @abstractmethod
    def render(self) -> str: ...

class SessionDialog(ABC):
    @abstractmethod
    def show(self) -> str: ...

class SessionCloudButton(SessionButton):
    def render(self) -> str: return "cloud-btn-session"

class SessionCloudDialog(SessionDialog):
    def show(self) -> str: return "cloud-dlg-session"

class SessionLocalButton(SessionButton):
    def render(self) -> str: return "local-btn-session"

class SessionLocalDialog(SessionDialog):
    def show(self) -> str: return "local-dlg-session"

class SessionUIFactory(ABC):
    @abstractmethod
    def create_button(self) -> SessionButton: ...
    @abstractmethod
    def create_dialog(self) -> SessionDialog: ...

class SessionCloudFactory(SessionUIFactory):
    def create_button(self) -> SessionButton: return SessionCloudButton()
    def create_dialog(self) -> SessionDialog: return SessionCloudDialog()

class SessionLocalFactory(SessionUIFactory):
    def create_button(self) -> SessionButton: return SessionLocalButton()
    def create_dialog(self) -> SessionDialog: return SessionLocalDialog()

def run_ui(factory: SessionUIFactory) -> str:
    return factory.create_button().render() + "|" + factory.create_dialog().show()
