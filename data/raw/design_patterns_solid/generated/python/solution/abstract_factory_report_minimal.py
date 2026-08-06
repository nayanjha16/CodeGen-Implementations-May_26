"""DesignPatternsSolid | kind=design_pattern | label=abstract factory | domain=report | tier=minimal"""
from __future__ import annotations

from abc import ABC, abstractmethod

class ReportButton(ABC):
    @abstractmethod
    def render(self) -> str: ...

class ReportDialog(ABC):
    @abstractmethod
    def show(self) -> str: ...

class ReportCloudButton(ReportButton):
    def render(self) -> str: return "cloud-btn-report"

class ReportCloudDialog(ReportDialog):
    def show(self) -> str: return "cloud-dlg-report"

class ReportLocalButton(ReportButton):
    def render(self) -> str: return "local-btn-report"

class ReportLocalDialog(ReportDialog):
    def show(self) -> str: return "local-dlg-report"

class ReportUIFactory(ABC):
    @abstractmethod
    def create_button(self) -> ReportButton: ...
    @abstractmethod
    def create_dialog(self) -> ReportDialog: ...

class ReportCloudFactory(ReportUIFactory):
    def create_button(self) -> ReportButton: return ReportCloudButton()
    def create_dialog(self) -> ReportDialog: return ReportCloudDialog()

class ReportLocalFactory(ReportUIFactory):
    def create_button(self) -> ReportButton: return ReportLocalButton()
    def create_dialog(self) -> ReportDialog: return ReportLocalDialog()

def run_ui(factory: ReportUIFactory) -> str:
    return factory.create_button().render() + "|" + factory.create_dialog().show()
