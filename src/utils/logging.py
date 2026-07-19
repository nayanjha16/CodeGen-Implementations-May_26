"""Logging configuration and shared progress helpers."""

from __future__ import annotations

import logging
import sys

TASK_LABELS: dict[str, str] = {
    "text2sql": "text2sql (Text-to-SQL)",
    "sql2nosql": "sql2nosql (SQL-to-MongoDB)",
    "nosql2doc": "nosql2doc (NoSQL-to-Documentation)",
    "documentation": "nosql2doc (NoSQL-to-Documentation)",
}


def task_label(task: str) -> str:
    """Return a human-readable label for a pipeline task name."""
    return TASK_LABELS.get(task.strip().lower(), task)


def setup_logging(level: int = logging.INFO) -> logging.Logger:
    """Configure project loggers and return the root ``codegen`` logger."""
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)

    logger = logging.getLogger("codegen")
    if not logger.handlers:
        logger.addHandler(handler)
    logger.setLevel(level)
    logger.propagate = False

    training_logger = logging.getLogger("codegen.training")
    training_logger.setLevel(level)

    return logger


def log_step(task: str, message: str, *args: object) -> None:
    """Log a single pipeline step with a consistent task prefix."""
    logging.getLogger("codegen").info("[%s] " + message, task_label(task), *args)


def log_batch_start(task: str, total: int) -> None:
    """Log the start of a batch generation pass."""
    if total <= 0:
        return
    log_step(task, "Starting generation (%d samples)", total)


def log_batch_progress(task: str, current: int, total: int, *, every: int = 25) -> None:
    """Log batch progress at coarse intervals to avoid noisy output."""
    if total <= 10 or every <= 0:
        return
    if current % every == 0 and current < total:
        logging.getLogger("codegen").info(
            "[%s] Progress: %d/%d (%.0f%%)",
            task_label(task),
            current,
            total,
            100 * current / total,
        )


def log_batch_done(task: str, total: int, *, valid: int | None = None) -> None:
    """Log completion of a batch generation pass."""
    if total <= 0:
        return
    if valid is None:
        log_step(task, "Completed %d samples", total)
    else:
        log_step(task, "Completed %d samples (%d valid)", total, valid)
