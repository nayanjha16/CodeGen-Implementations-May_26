"""Load and merge deployment manifest with environment overrides."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

import yaml

from hf_deploy import INTENTS, MANIFEST_PATH, REPO_ROOT


def _as_bool(value: str | None, default: bool) -> bool:
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def resolve_hub_adapter_ids(hub: dict[str, Any]) -> dict[str, str]:
    """Map intent → ``namespace/repo`` Hub ids."""
    org = str(hub.get("org") or os.getenv("HF_ORG") or "").strip()
    repos = hub.get("repos") or {}
    resolved: dict[str, str] = {}
    for intent in INTENTS:
        repo = str(repos.get(intent, f"codegen-350M-{intent}-lora")).strip()
        if "/" in repo:
            resolved[intent] = repo
        elif not org:
            raise ValueError(
                f"Hub adapter '{repo}' needs hub.org / HF_ORG (e.g. care2achieve)."
            )
        else:
            resolved[intent] = f"{org}/{repo}"
    return resolved


def load_manifest(path: Path | None = None) -> dict[str, Any]:
    """Load ``manifest.yaml`` and apply ``HF_DEPLOY_*`` env overrides."""
    manifest_path = path or MANIFEST_PATH
    with manifest_path.open(encoding="utf-8") as handle:
        data = yaml.safe_load(handle) or {}

    data["base_model"] = os.getenv(
        "HF_DEPLOY_BASE_MODEL",
        data.get("base_model", "Salesforce/codegen-350M-multi"),
    )
    data["checkpoint_version"] = os.getenv(
        "HF_DEPLOY_CHECKPOINT_VERSION",
        data.get("checkpoint_version", "v3"),
    )

    source = os.getenv(
        "HF_DEPLOY_ADAPTER_SOURCE",
        data.get("adapter_source", "local"),
    )
    data["adapter_source"] = str(source).strip().lower()

    checkpoints_root = os.getenv(
        "HF_DEPLOY_CHECKPOINTS_ROOT",
        data.get("checkpoints_root", "models/checkpoints"),
    )
    root_path = Path(checkpoints_root)
    if not root_path.is_absolute():
        root_path = REPO_ROOT / root_path
    data["checkpoints_root"] = root_path

    data["eager_load"] = _as_bool(os.getenv("HF_DEPLOY_EAGER_LOAD"), True)
    data["device"] = os.getenv("HF_DEPLOY_DEVICE", "auto")

    classifier = dict(data.get("classifier") or {})
    threshold = os.getenv("HF_DEPLOY_CONFIDENCE_THRESHOLD")
    if threshold is not None:
        classifier["confidence_threshold"] = float(threshold)
    data["classifier"] = classifier

    adapters = data.get("adapters") or {name: name for name in INTENTS}
    data["adapters"] = {str(k): str(v) for k, v in adapters.items()}
    data.setdefault("generation", {})
    hub = dict(data.get("hub") or {})
    if os.getenv("HF_ORG"):
        hub["org"] = os.getenv("HF_ORG")
    data["hub"] = hub
    data["hub_adapter_ids"] = resolve_hub_adapter_ids(hub)
    return data
