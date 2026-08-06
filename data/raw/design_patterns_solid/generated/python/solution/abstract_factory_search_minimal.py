"""DesignPatternsSolid | kind=design_pattern | label=abstract factory | domain=search | tier=minimal"""
from __future__ import annotations

from abc import ABC, abstractmethod

class SearchButton(ABC):
    @abstractmethod
    def render(self) -> str: ...

class SearchDialog(ABC):
    @abstractmethod
    def show(self) -> str: ...

class SearchCloudButton(SearchButton):
    def render(self) -> str: return "cloud-btn-search"

class SearchCloudDialog(SearchDialog):
    def show(self) -> str: return "cloud-dlg-search"

class SearchLocalButton(SearchButton):
    def render(self) -> str: return "local-btn-search"

class SearchLocalDialog(SearchDialog):
    def show(self) -> str: return "local-dlg-search"

class SearchUIFactory(ABC):
    @abstractmethod
    def create_button(self) -> SearchButton: ...
    @abstractmethod
    def create_dialog(self) -> SearchDialog: ...

class SearchCloudFactory(SearchUIFactory):
    def create_button(self) -> SearchButton: return SearchCloudButton()
    def create_dialog(self) -> SearchDialog: return SearchCloudDialog()

class SearchLocalFactory(SearchUIFactory):
    def create_button(self) -> SearchButton: return SearchLocalButton()
    def create_dialog(self) -> SearchDialog: return SearchLocalDialog()

def run_ui(factory: SearchUIFactory) -> str:
    return factory.create_button().render() + "|" + factory.create_dialog().show()
