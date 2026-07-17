"""Desktop entry point — run from repo root."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from dotenv import load_dotenv

from tool.config import TOOL_DIR
from tool.core.embedding_cache import configure_hf_cache

load_dotenv(TOOL_DIR / ".env")
configure_hf_cache()

from tool.desktop.main_window import run_desktop

if __name__ == "__main__":
    run_desktop()
