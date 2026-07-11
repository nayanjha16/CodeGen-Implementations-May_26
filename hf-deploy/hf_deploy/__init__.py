"""Multi-adapter Hugging Face deployment package."""

from __future__ import annotations

from pathlib import Path

PACKAGE_ROOT = Path(__file__).resolve().parent
HF_DEPLOY_ROOT = PACKAGE_ROOT.parent
REPO_ROOT = HF_DEPLOY_ROOT.parent
MANIFEST_PATH = HF_DEPLOY_ROOT / "manifest.yaml"

INTENTS = ("text2sql", "sql2nosql", "nosql2doc")
CLARIFY_INTENT = "clarify"

__all__ = [
    "CLARIFY_INTENT",
    "HF_DEPLOY_ROOT",
    "INTENTS",
    "MANIFEST_PATH",
    "PACKAGE_ROOT",
    "REPO_ROOT",
]
