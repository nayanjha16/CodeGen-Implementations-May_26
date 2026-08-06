"""DesignPatternsSolid | kind=design_pattern | label=abstract factory | domain=sms | tier=minimal"""
from __future__ import annotations

from abc import ABC, abstractmethod

class SmsButton(ABC):
    @abstractmethod
    def render(self) -> str: ...

class SmsDialog(ABC):
    @abstractmethod
    def show(self) -> str: ...

class SmsCloudButton(SmsButton):
    def render(self) -> str: return "cloud-btn-sms"

class SmsCloudDialog(SmsDialog):
    def show(self) -> str: return "cloud-dlg-sms"

class SmsLocalButton(SmsButton):
    def render(self) -> str: return "local-btn-sms"

class SmsLocalDialog(SmsDialog):
    def show(self) -> str: return "local-dlg-sms"

class SmsUIFactory(ABC):
    @abstractmethod
    def create_button(self) -> SmsButton: ...
    @abstractmethod
    def create_dialog(self) -> SmsDialog: ...

class SmsCloudFactory(SmsUIFactory):
    def create_button(self) -> SmsButton: return SmsCloudButton()
    def create_dialog(self) -> SmsDialog: return SmsCloudDialog()

class SmsLocalFactory(SmsUIFactory):
    def create_button(self) -> SmsButton: return SmsLocalButton()
    def create_dialog(self) -> SmsDialog: return SmsLocalDialog()

def run_ui(factory: SmsUIFactory) -> str:
    return factory.create_button().render() + "|" + factory.create_dialog().show()
