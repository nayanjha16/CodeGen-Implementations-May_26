"""DesignPatternsSolid | kind=design_pattern | label=abstract factory | domain=notifications | tier=minimal"""
from __future__ import annotations

from abc import ABC, abstractmethod

class NotificationsButton(ABC):
    @abstractmethod
    def render(self) -> str: ...

class NotificationsDialog(ABC):
    @abstractmethod
    def show(self) -> str: ...

class NotificationsCloudButton(NotificationsButton):
    def render(self) -> str: return "cloud-btn-notifications"

class NotificationsCloudDialog(NotificationsDialog):
    def show(self) -> str: return "cloud-dlg-notifications"

class NotificationsLocalButton(NotificationsButton):
    def render(self) -> str: return "local-btn-notifications"

class NotificationsLocalDialog(NotificationsDialog):
    def show(self) -> str: return "local-dlg-notifications"

class NotificationsUIFactory(ABC):
    @abstractmethod
    def create_button(self) -> NotificationsButton: ...
    @abstractmethod
    def create_dialog(self) -> NotificationsDialog: ...

class NotificationsCloudFactory(NotificationsUIFactory):
    def create_button(self) -> NotificationsButton: return NotificationsCloudButton()
    def create_dialog(self) -> NotificationsDialog: return NotificationsCloudDialog()

class NotificationsLocalFactory(NotificationsUIFactory):
    def create_button(self) -> NotificationsButton: return NotificationsLocalButton()
    def create_dialog(self) -> NotificationsDialog: return NotificationsLocalDialog()

def run_ui(factory: NotificationsUIFactory) -> str:
    return factory.create_button().render() + "|" + factory.create_dialog().show()
