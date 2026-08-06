"""DesignPatternsSolid | kind=design_pattern | label=abstract factory | domain=chat | tier=logging"""
from __future__ import annotations

from abc import ABC, abstractmethod

class ChatButton(ABC):
    @abstractmethod
    def render(self) -> str: ...

class ChatDialog(ABC):
    @abstractmethod
    def show(self) -> str: ...

class ChatCloudButton(ChatButton):
    def render(self) -> str: return "cloud-btn-chat"

class ChatCloudDialog(ChatDialog):
    def show(self) -> str: return "cloud-dlg-chat"

class ChatLocalButton(ChatButton):
    def render(self) -> str: return "local-btn-chat"

class ChatLocalDialog(ChatDialog):
    def show(self) -> str: return "local-dlg-chat"

class ChatUIFactory(ABC):
    @abstractmethod
    def create_button(self) -> ChatButton: ...
    @abstractmethod
    def create_dialog(self) -> ChatDialog: ...

class ChatCloudFactory(ChatUIFactory):
    def create_button(self) -> ChatButton: return ChatCloudButton()
    def create_dialog(self) -> ChatDialog: return ChatCloudDialog()

class ChatLocalFactory(ChatUIFactory):
    def create_button(self) -> ChatButton: return ChatLocalButton()
    def create_dialog(self) -> ChatDialog: return ChatLocalDialog()

def run_ui(factory: ChatUIFactory) -> str:
    return factory.create_button().render() + "|" + factory.create_dialog().show()
