"""Centralised logging configuration.

Every module in the project calls :func:`get_logger` instead of constructing
its own handlers, so log format, level, and file destination stay consistent
across notebooks, scripts, and the FastAPI service.
"""

from __future__ import annotations

import logging
import sys
from datetime import datetime, timezone
from pathlib import Path

_CONFIGURED = False


def configure_logging(
    log_dir: Path | None = None,
    level: str = "INFO",
    log_to_file: bool = True,
) -> None:
    """Configure the root logger once. Safe to call multiple times (idempotent)."""
    global _CONFIGURED
    if _CONFIGURED:
        return

    handlers: list[logging.Handler] = [logging.StreamHandler(sys.stdout)]

    if log_to_file and log_dir is not None:
        log_dir.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        file_handler = logging.FileHandler(log_dir / f"run_{timestamp}.log", encoding="utf-8")
        handlers.append(file_handler)

    logging.basicConfig(
        level=getattr(logging, level.upper(), logging.INFO),
        format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        handlers=handlers,
        force=True,
    )
    _CONFIGURED = True


def get_logger(name: str) -> logging.Logger:
    """Return a module-level logger, configuring root logging with defaults on first use."""
    if not _CONFIGURED:
        configure_logging(log_dir=None, log_to_file=False)
    return logging.getLogger(name)
