"""Load and merge the deployment manifest with environment overrides.

Every setting has three layers (last wins):
    1. ``manifest.yaml`` value
    2. ``CODEGEN_*`` environment variable
    3. Hardcoded fallback (so the app still boots without a manifest)
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

import yaml

from codegen_api import DEPLOY_ROOT, INTENTS, MANIFEST_PATH, REPO_ROOT


def _as_bool(value: str | None, default: bool) -> bool:
    """Parse an env string into a bool, falling back to ``default``."""
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def load_dotenv(path: Path | None = None) -> None:
    """Load ``fastapi-deploy/.env`` into the environment if present.

    Simple KEY=VALUE parser (no external dependency). Real environment
    variables already set take priority, so ``.env`` only fills gaps.
    """
    env_path = path or (DEPLOY_ROOT / ".env")
    if not env_path.exists():
        return
    for line in env_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


def resolve_hub_adapter_ids(hub: dict[str, Any]) -> dict[str, str]:
    """Map each intent to its ``namespace/repo`` Hugging Face Hub id."""
    org = str(hub.get("org", "") or os.getenv("HF_ORG", "")).strip()
    repos = hub.get("repos") or {}
    resolved: dict[str, str] = {}
    for intent in INTENTS:
        repo = repos.get(intent) or f"codegen-350M-{intent}-lora"
        if "/" not in repo:
            if not org:
                raise ValueError(
                    f"Hub adapter '{intent}' needs hub.org / HF_ORG "
                    "(e.g. codegenstudio)."
                )
            repo = f"{org}/{repo}"
        resolved[intent] = repo
    return resolved


def load_manifest(path: Path | None = None) -> dict[str, Any]:
    """Load ``manifest.yaml`` and apply ``CODEGEN_*`` env overrides."""
    load_dotenv()
    manifest_path = path or MANIFEST_PATH
    data: dict[str, Any] = {}
    if manifest_path.exists():
        with open(manifest_path, "r", encoding="utf-8") as handle:
            data = yaml.safe_load(handle) or {}

    data["base_model"] = os.getenv(
        "CODEGEN_BASE_MODEL",
        data.get("base_model", "Salesforce/codegen-350M-multi"),
    )
    data["checkpoint_version"] = os.getenv(
        "CODEGEN_CHECKPOINT_VERSION",
        data.get("checkpoint_version", "v3"),
    )

    source = os.getenv(
        "CODEGEN_ADAPTER_SOURCE",
        data.get("adapter_source", "local"),
    )
    data["adapter_source"] = source.strip().lower()

    root_value = os.getenv(
        "CODEGEN_CHECKPOINTS_ROOT",
        data.get("checkpoints_root", "models/checkpoints"),
    )
    root_path = Path(root_value)
    if not root_path.is_absolute():
        root_path = REPO_ROOT / root_path
    data["checkpoints_root"] = str(root_path)

    data["eager_load"] = _as_bool(
        os.getenv("CODEGEN_EAGER_LOAD"),
        bool(data.get("eager_load", True)),
    )
    data["device"] = os.getenv("CODEGEN_DEVICE", data.get("device", "auto"))

    classifier = dict(data.get("classifier") or {})
    classifier["confidence_threshold"] = float(
        os.getenv(
            "CODEGEN_CONFIDENCE_THRESHOLD",
            classifier.get("confidence_threshold", 0.45),
        )
    )
    classifier.setdefault("prefer_rules", True)
    data["classifier"] = classifier

    adapters = dict(data.get("adapters") or {})
    for intent in INTENTS:
        adapters.setdefault(intent, intent)
    data["adapters"] = adapters

    data["generation"] = dict(data.get("generation") or {})

    hub = dict(data.get("hub") or {})
    env_org = os.getenv("HF_ORG")
    if env_org:
        hub["org"] = env_org
    data["hub"] = hub
    data["hub_adapter_ids"] = resolve_hub_adapter_ids(hub)

    return data
