"""DesignPatternsSolid | kind=design_pattern | label=abstract factory | domain=auth | tier=logging"""
from __future__ import annotations

from abc import ABC, abstractmethod

class AuthButton(ABC):
    @abstractmethod
    def render(self) -> str: ...

class AuthDialog(ABC):
    @abstractmethod
    def show(self) -> str: ...

class AuthCloudButton(AuthButton):
    def render(self) -> str: return "cloud-btn-auth"

class AuthCloudDialog(AuthDialog):
    def show(self) -> str: return "cloud-dlg-auth"

class AuthLocalButton(AuthButton):
    def render(self) -> str: return "local-btn-auth"

class AuthLocalDialog(AuthDialog):
    def show(self) -> str: return "local-dlg-auth"

class AuthUIFactory(ABC):
    @abstractmethod
    def create_button(self) -> AuthButton: ...
    @abstractmethod
    def create_dialog(self) -> AuthDialog: ...

class AuthCloudFactory(AuthUIFactory):
    def create_button(self) -> AuthButton: return AuthCloudButton()
    def create_dialog(self) -> AuthDialog: return AuthCloudDialog()

class AuthLocalFactory(AuthUIFactory):
    def create_button(self) -> AuthButton: return AuthLocalButton()
    def create_dialog(self) -> AuthDialog: return AuthLocalDialog()

def run_ui(factory: AuthUIFactory) -> str:
    return factory.create_button().render() + "|" + factory.create_dialog().show()
