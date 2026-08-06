"""DesignPatternsSolid | kind=design_pattern | label=abstract factory | domain=profile | tier=minimal"""
from __future__ import annotations

from abc import ABC, abstractmethod

class ProfileButton(ABC):
    @abstractmethod
    def render(self) -> str: ...

class ProfileDialog(ABC):
    @abstractmethod
    def show(self) -> str: ...

class ProfileCloudButton(ProfileButton):
    def render(self) -> str: return "cloud-btn-profile"

class ProfileCloudDialog(ProfileDialog):
    def show(self) -> str: return "cloud-dlg-profile"

class ProfileLocalButton(ProfileButton):
    def render(self) -> str: return "local-btn-profile"

class ProfileLocalDialog(ProfileDialog):
    def show(self) -> str: return "local-dlg-profile"

class ProfileUIFactory(ABC):
    @abstractmethod
    def create_button(self) -> ProfileButton: ...
    @abstractmethod
    def create_dialog(self) -> ProfileDialog: ...

class ProfileCloudFactory(ProfileUIFactory):
    def create_button(self) -> ProfileButton: return ProfileCloudButton()
    def create_dialog(self) -> ProfileDialog: return ProfileCloudDialog()

class ProfileLocalFactory(ProfileUIFactory):
    def create_button(self) -> ProfileButton: return ProfileLocalButton()
    def create_dialog(self) -> ProfileDialog: return ProfileLocalDialog()

def run_ui(factory: ProfileUIFactory) -> str:
    return factory.create_button().render() + "|" + factory.create_dialog().show()
