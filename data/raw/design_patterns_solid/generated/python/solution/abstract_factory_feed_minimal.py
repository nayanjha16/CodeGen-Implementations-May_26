"""DesignPatternsSolid | kind=design_pattern | label=abstract factory | domain=feed | tier=minimal"""
from __future__ import annotations

from abc import ABC, abstractmethod

class FeedButton(ABC):
    @abstractmethod
    def render(self) -> str: ...

class FeedDialog(ABC):
    @abstractmethod
    def show(self) -> str: ...

class FeedCloudButton(FeedButton):
    def render(self) -> str: return "cloud-btn-feed"

class FeedCloudDialog(FeedDialog):
    def show(self) -> str: return "cloud-dlg-feed"

class FeedLocalButton(FeedButton):
    def render(self) -> str: return "local-btn-feed"

class FeedLocalDialog(FeedDialog):
    def show(self) -> str: return "local-dlg-feed"

class FeedUIFactory(ABC):
    @abstractmethod
    def create_button(self) -> FeedButton: ...
    @abstractmethod
    def create_dialog(self) -> FeedDialog: ...

class FeedCloudFactory(FeedUIFactory):
    def create_button(self) -> FeedButton: return FeedCloudButton()
    def create_dialog(self) -> FeedDialog: return FeedCloudDialog()

class FeedLocalFactory(FeedUIFactory):
    def create_button(self) -> FeedButton: return FeedLocalButton()
    def create_dialog(self) -> FeedDialog: return FeedLocalDialog()

def run_ui(factory: FeedUIFactory) -> str:
    return factory.create_button().render() + "|" + factory.create_dialog().show()
