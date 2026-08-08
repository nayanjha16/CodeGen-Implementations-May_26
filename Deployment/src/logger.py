"""Per-subprocess logging: a timestamped UTF-8 file plus a quieter console.

Each entry point calls ``setup_logging()`` once. The log file is named after the
running script (``<script>_<YYYYMMDD>_<HHMMSS>.log``) so a full pipeline run
leaves one labelled file per stage (plan.md §13). File gets INFO+, console WARNING+.
"""

from __future__ import annotations

import logging
import sys
from datetime import datetime
from pathlib import Path

from . import config


def setup_logging(prefix: str | None = None) -> Path:
    """Configure root logging and return the log file path.

    prefix: overrides the auto-derived script name (useful for notebooks/tests).
    """
    config.ensure_dirs()

    if prefix is None:
        argv0 = sys.argv[0] if sys.argv and sys.argv[0] else "session"
        prefix = Path(argv0).stem or "session"

    # datetime.now() is fine here — this is a log filename, not cached content.
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_path = config.LOGS_DIR / f"{prefix}_{stamp}.log"

    root = logging.getLogger()
    root.setLevel(logging.INFO)
    # Clear any handlers a prior call (or a library) installed, so repeated
    # setup in one process doesn't double-log.
    for h in list(root.handlers):
        root.removeHandler(h)

    fmt = logging.Formatter(
        "%(asctime)s [%(levelname)-7s] [%(name)s] %(message)s"
    )

    file_handler = logging.FileHandler(log_path, encoding="utf-8")
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(fmt)
    root.addHandler(file_handler)

    console = logging.StreamHandler(sys.stderr)
    console.setLevel(logging.WARNING)  # keep the terminal clean during long runs
    console.setFormatter(fmt)
    root.addHandler(console)

    logging.getLogger(__name__).info("log file: %s", log_path)
    return log_path
