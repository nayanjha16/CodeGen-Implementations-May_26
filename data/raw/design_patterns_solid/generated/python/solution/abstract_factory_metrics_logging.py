"""DesignPatternsSolid | kind=design_pattern | label=abstract factory | domain=metrics | tier=logging"""
from __future__ import annotations

from abc import ABC, abstractmethod

class MetricsButton(ABC):
    @abstractmethod
    def render(self) -> str: ...

class MetricsDialog(ABC):
    @abstractmethod
    def show(self) -> str: ...

class MetricsCloudButton(MetricsButton):
    def render(self) -> str: return "cloud-btn-metrics"

class MetricsCloudDialog(MetricsDialog):
    def show(self) -> str: return "cloud-dlg-metrics"

class MetricsLocalButton(MetricsButton):
    def render(self) -> str: return "local-btn-metrics"

class MetricsLocalDialog(MetricsDialog):
    def show(self) -> str: return "local-dlg-metrics"

class MetricsUIFactory(ABC):
    @abstractmethod
    def create_button(self) -> MetricsButton: ...
    @abstractmethod
    def create_dialog(self) -> MetricsDialog: ...

class MetricsCloudFactory(MetricsUIFactory):
    def create_button(self) -> MetricsButton: return MetricsCloudButton()
    def create_dialog(self) -> MetricsDialog: return MetricsCloudDialog()

class MetricsLocalFactory(MetricsUIFactory):
    def create_button(self) -> MetricsButton: return MetricsLocalButton()
    def create_dialog(self) -> MetricsDialog: return MetricsLocalDialog()

def run_ui(factory: MetricsUIFactory) -> str:
    return factory.create_button().render() + "|" + factory.create_dialog().show()
