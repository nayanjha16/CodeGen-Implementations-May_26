"""FR-5 retry helpers for failed SQL execution."""

from __future__ import annotations

from dataclasses import dataclass

from agent.config.settings import AgentSettings, get_settings


@dataclass
class RetryState:
    attempt: int = 0
    max_retries: int = 3
    last_sql: str | None = None
    last_error: str | None = None

    @classmethod
    def from_settings(cls, settings: AgentSettings | None = None) -> RetryState:
        cfg = settings or get_settings()
        return cls(max_retries=cfg.max_retries)

    @property
    def exhausted(self) -> bool:
        return self.attempt >= self.max_retries

    def can_retry(self) -> bool:
        return (
            not self.exhausted
            and bool(self.last_sql)
            and bool(self.last_error)
        )

    def record_failure(self, *, sql: str, error: str) -> RetryState:
        self.attempt += 1
        self.last_sql = sql
        self.last_error = error
        return self

    def reset(self) -> RetryState:
        self.attempt = 0
        self.last_sql = None
        self.last_error = None
        return self


def should_retry_sql(state: RetryState, *, success: bool) -> bool:
    if success:
        return False
    return state.attempt < state.max_retries
