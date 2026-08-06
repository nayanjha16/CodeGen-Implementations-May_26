"""DesignPatternsSolid | kind=design_pattern | label=abstract factory | domain=logging | tier=errors"""
from __future__ import annotations

from abc import ABC, abstractmethod

class LoggingButton(ABC):
    @abstractmethod
    def render(self) -> str: ...

class LoggingDialog(ABC):
    @abstractmethod
    def show(self) -> str: ...

class LoggingCloudButton(LoggingButton):
    def render(self) -> str: return "cloud-btn-logging"

class LoggingCloudDialog(LoggingDialog):
    def show(self) -> str: return "cloud-dlg-logging"

class LoggingLocalButton(LoggingButton):
    def render(self) -> str: return "local-btn-logging"

class LoggingLocalDialog(LoggingDialog):
    def show(self) -> str: return "local-dlg-logging"

class LoggingUIFactory(ABC):
    @abstractmethod
    def create_button(self) -> LoggingButton: ...
    @abstractmethod
    def create_dialog(self) -> LoggingDialog: ...

class LoggingCloudFactory(LoggingUIFactory):
    def create_button(self) -> LoggingButton: return LoggingCloudButton()
    def create_dialog(self) -> LoggingDialog: return LoggingCloudDialog()

class LoggingLocalFactory(LoggingUIFactory):
    def create_button(self) -> LoggingButton: return LoggingLocalButton()
    def create_dialog(self) -> LoggingDialog: return LoggingLocalDialog()

def run_ui(factory: LoggingUIFactory) -> str:
    return factory.create_button().render() + "|" + factory.create_dialog().show()
