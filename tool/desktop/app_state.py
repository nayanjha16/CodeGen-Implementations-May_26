"""Shared application state for the desktop UI."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import pandas as pd

from tool.core.activity_logger import ActivityLogger
from tool.core.settings_store import AppSettings, SettingsStore


@dataclass
class AppState:
    logger: ActivityLogger = field(default_factory=ActivityLogger)
    settings: AppSettings | None = None
    generated_sql: str | None = None
    validation_status: dict[str, Any] | None = None
    result_df: pd.DataFrame | None = None
    result_meta: dict[str, Any] = field(default_factory=dict)
    selected_tables: list[str] = field(default_factory=list)

    def load_settings(self) -> AppSettings:
        self.settings = SettingsStore().load()
        return self.settings

    def clear_query(self, *, clear_log: bool = True) -> None:
        self.generated_sql = None
        self.validation_status = None
        self.result_df = None
        self.result_meta = {}
        self.selected_tables = []
        if clear_log:
            self.logger.clear()

    def apply_result(self, result) -> None:
        self.generated_sql = result.generated_sql
        self.validation_status = result.validation_status
        self.result_df = result.result_df
        self.result_meta = result.result_meta or {}
        self.selected_tables = result.selected_tables or []
