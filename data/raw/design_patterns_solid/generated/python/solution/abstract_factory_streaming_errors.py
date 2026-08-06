"""DesignPatternsSolid | kind=design_pattern | label=abstract factory | domain=streaming | tier=errors"""
from __future__ import annotations

from abc import ABC, abstractmethod

class StreamingButton(ABC):
    @abstractmethod
    def render(self) -> str: ...

class StreamingDialog(ABC):
    @abstractmethod
    def show(self) -> str: ...

class StreamingCloudButton(StreamingButton):
    def render(self) -> str: return "cloud-btn-streaming"

class StreamingCloudDialog(StreamingDialog):
    def show(self) -> str: return "cloud-dlg-streaming"

class StreamingLocalButton(StreamingButton):
    def render(self) -> str: return "local-btn-streaming"

class StreamingLocalDialog(StreamingDialog):
    def show(self) -> str: return "local-dlg-streaming"

class StreamingUIFactory(ABC):
    @abstractmethod
    def create_button(self) -> StreamingButton: ...
    @abstractmethod
    def create_dialog(self) -> StreamingDialog: ...

class StreamingCloudFactory(StreamingUIFactory):
    def create_button(self) -> StreamingButton: return StreamingCloudButton()
    def create_dialog(self) -> StreamingDialog: return StreamingCloudDialog()

class StreamingLocalFactory(StreamingUIFactory):
    def create_button(self) -> StreamingButton: return StreamingLocalButton()
    def create_dialog(self) -> StreamingDialog: return StreamingLocalDialog()

def run_ui(factory: StreamingUIFactory) -> str:
    return factory.create_button().render() + "|" + factory.create_dialog().show()
