"""FastAPI multi-adapter deployment package.

Serves ``Salesforce/codegen-350M-multi`` plus three LoRA adapters behind an
OpenAI-compatible API.
"""

from __future__ import annotations

from pathlib import Path

# fastapi-deploy/codegen_api/__init__.py -> package -> deploy folder -> repo
PACKAGE_ROOT = Path(__file__).resolve().parent
DEPLOY_ROOT = PACKAGE_ROOT.parent
REPO_ROOT = DEPLOY_ROOT.parent
MANIFEST_PATH = DEPLOY_ROOT / "manifest.yaml"

# The three fine-tuned tasks, in routing/loading order.
INTENTS: tuple[str, ...] = ("text2sql", "sql2nosql", "nosql2doc")

# Returned when the classifier is not confident enough to route.
CLARIFY_INTENT = "clarify"

__all__ = [
    "PACKAGE_ROOT",
    "DEPLOY_ROOT",
    "REPO_ROOT",
    "MANIFEST_PATH",
    "INTENTS",
    "CLARIFY_INTENT",
]
