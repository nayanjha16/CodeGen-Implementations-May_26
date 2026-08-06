"""DesignPatternsSolid | kind=design_pattern | label=abstract factory | domain=map | tier=minimal"""
from __future__ import annotations

from abc import ABC, abstractmethod

class MapButton(ABC):
    @abstractmethod
    def render(self) -> str: ...

class MapDialog(ABC):
    @abstractmethod
    def show(self) -> str: ...

class MapCloudButton(MapButton):
    def render(self) -> str: return "cloud-btn-map"

class MapCloudDialog(MapDialog):
    def show(self) -> str: return "cloud-dlg-map"

class MapLocalButton(MapButton):
    def render(self) -> str: return "local-btn-map"

class MapLocalDialog(MapDialog):
    def show(self) -> str: return "local-dlg-map"

class MapUIFactory(ABC):
    @abstractmethod
    def create_button(self) -> MapButton: ...
    @abstractmethod
    def create_dialog(self) -> MapDialog: ...

class MapCloudFactory(MapUIFactory):
    def create_button(self) -> MapButton: return MapCloudButton()
    def create_dialog(self) -> MapDialog: return MapCloudDialog()

class MapLocalFactory(MapUIFactory):
    def create_button(self) -> MapButton: return MapLocalButton()
    def create_dialog(self) -> MapDialog: return MapLocalDialog()

def run_ui(factory: MapUIFactory) -> str:
    return factory.create_button().render() + "|" + factory.create_dialog().show()
