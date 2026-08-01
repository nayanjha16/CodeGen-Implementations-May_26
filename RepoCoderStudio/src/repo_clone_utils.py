"""
============================================================
RepoCoder Studio
repo_clone_utils.py — shared real-repo cloning helper
============================================================

One small, shared helper for the external-benchmark evaluation modules
that need a real, disk-resident checkout of a real GitHub repository at
a specific commit: src/swebench_localization.py (file-localization) and
src/realworld_rag_generation_eval.py (RAG-grounded generation quality).
Both need the exact same "clone cheaply, checkout one commit" operation,
so it lives here once instead of twice.

Uses a partial clone (--filter=blob:none, no full object history) plus
a single checkout -- verified live against a real repo (psf/requests):
~8 seconds, 6.4MB for a small repo, instead of downloading the entire
commit history a normal `git clone` would fetch.
"""

from __future__ import annotations

import subprocess
from pathlib import Path

from src.logger import LOG

CLONE_TIMEOUT_SECONDS = 180


def clone_at_commit(repo: str, base_commit: str, dest: Path) -> bool:
    """Partial clone + checkout of one commit of a GitHub repo (repo is
    "owner/name", as SWE-bench/RepoBench's `repo`/`repo_name` fields use).
    Returns False (logged, not raised) on any failure -- callers treat a
    failed clone as "skip this instance," not a hard error, since this is
    always best-effort external evaluation data."""
    url = f"https://github.com/{repo}.git"
    try:
        subprocess.run(
            ["git", "clone", "--filter=blob:none", "--no-checkout", url, str(dest)],
            check=True, capture_output=True, timeout=CLONE_TIMEOUT_SECONDS,
        )
        subprocess.run(
            ["git", "-C", str(dest), "checkout", base_commit],
            check=True, capture_output=True, timeout=CLONE_TIMEOUT_SECONDS,
        )
        return True
    except Exception as exc:
        LOG.warning(f"Could not clone/checkout {repo}@{base_commit}: {exc}")
        return False
