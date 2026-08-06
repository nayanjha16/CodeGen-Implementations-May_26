"""DesignPatternsSolid | kind=design_pattern | label=abstract factory | domain=video | tier=logging"""
from __future__ import annotations

from abc import ABC, abstractmethod

class VideoButton(ABC):
    @abstractmethod
    def render(self) -> str: ...

class VideoDialog(ABC):
    @abstractmethod
    def show(self) -> str: ...

class VideoCloudButton(VideoButton):
    def render(self) -> str: return "cloud-btn-video"

class VideoCloudDialog(VideoDialog):
    def show(self) -> str: return "cloud-dlg-video"

class VideoLocalButton(VideoButton):
    def render(self) -> str: return "local-btn-video"

class VideoLocalDialog(VideoDialog):
    def show(self) -> str: return "local-dlg-video"

class VideoUIFactory(ABC):
    @abstractmethod
    def create_button(self) -> VideoButton: ...
    @abstractmethod
    def create_dialog(self) -> VideoDialog: ...

class VideoCloudFactory(VideoUIFactory):
    def create_button(self) -> VideoButton: return VideoCloudButton()
    def create_dialog(self) -> VideoDialog: return VideoCloudDialog()

class VideoLocalFactory(VideoUIFactory):
    def create_button(self) -> VideoButton: return VideoLocalButton()
    def create_dialog(self) -> VideoDialog: return VideoLocalDialog()

def run_ui(factory: VideoUIFactory) -> str:
    return factory.create_button().render() + "|" + factory.create_dialog().show()
