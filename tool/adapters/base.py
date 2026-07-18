"""Query adapter protocol for tab extensibility."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Protocol

import pandas as pd

from tool.core.activity_logger import ActivityLogger


@dataclass
class ExecuteResult:
    success: bool
    generated_sql: str | None = None
    generated_nosql: str | None = None
    documentation: str | None = None
    validation_status: dict[str, Any] | None = None
    result_df: pd.DataFrame | None = None
    result_meta: dict[str, Any] = field(default_factory=dict)
    selected_tables: list[str] = field(default_factory=list)
    error: str | None = None


class QueryAdapter(Protocol):
    name: str

    def execute(self, user_input: str, *, logger: ActivityLogger) -> ExecuteResult: ...
