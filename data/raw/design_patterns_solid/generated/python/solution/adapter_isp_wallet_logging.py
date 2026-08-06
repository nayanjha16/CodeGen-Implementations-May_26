"""DesignPatternsSolid | kind=combo | label=adapter+isp | domain=wallet | tier=logging"""
from __future__ import annotations

class WalletLegacyApi:
    def legacy_fetch(self) -> str:
        return "LEGACY-wallet"

class WalletTarget:
    def fetch(self) -> str:
        raise NotImplementedError

class WalletAdapter(WalletTarget):
    def __init__(self, legacy: WalletLegacyApi) -> None:
        self._legacy = legacy

    def fetch(self) -> str:
        raw = self._legacy.legacy_fetch()
        return raw.lower().replace("legacy-", "modern-")
