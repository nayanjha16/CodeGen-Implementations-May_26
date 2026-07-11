#!/usr/bin/env python3
"""Publish selected checkpoint adapters to the Hugging Face Hub.

Usage (from repo root):

    PYTHONPATH=hf-deploy python hf-deploy/publish/push_adapters.py
    PYTHONPATH=hf-deploy python hf-deploy/publish/push_adapters.py --dry-run
    PYTHONPATH=hf-deploy python hf-deploy/publish/push_adapters.py --version v3
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = ROOT.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from hf_deploy import INTENTS  # noqa: E402
from hf_deploy.adapters.resolve import resolve_version_adapters  # noqa: E402
from hf_deploy.config import load_manifest  # noqa: E402

_UPLOAD_FILES = (
    "adapter_config.json",
    "adapter_model.safetensors",
    "adapter_model.bin",
)


def _load_env_files() -> None:
    """Load tokens from hf-deploy/.env then repo .env (without overriding shell)."""
    try:
        from dotenv import load_dotenv
    except ImportError:
        return
    load_dotenv(ROOT / ".env", override=False)
    load_dotenv(REPO_ROOT / ".env", override=False)


def _resolve_hf_token() -> str | None:
    return (
        os.getenv("HF_TOKEN")
        or os.getenv("HUGGING_FACE_HUB_TOKEN")
        or os.getenv("HUGGINGFACE_HUB_TOKEN")
    )


def _namespace(api: object | None = None, org: str = "") -> str:
    """Return Hub namespace: HF_ORG / manifest org, else authenticated username."""
    explicit = (org or os.getenv("HF_ORG") or "").strip()
    if explicit:
        return explicit
    if api is None:
        raise RuntimeError("Cannot resolve Hub namespace without an authenticated HfApi.")
    info = api.whoami()  # type: ignore[attr-defined]
    name = (info or {}).get("name")
    if not name:
        raise RuntimeError(
            "Could not resolve Hugging Face username from token. "
            "Set hub.org in manifest.yaml or HF_ORG in .env."
        )
    return str(name)


def _repo_id(namespace: str, name: str) -> str:
    name = name.strip()
    if "/" in name:
        return name
    namespace = namespace.strip()
    if not namespace:
        raise ValueError(f"Hub repo name '{name}' needs a namespace (user or org).")
    return f"{namespace}/{name}"


def _model_card(intent: str, base_model: str, version: str, repo_id: str) -> str:
    """Hub-valid README (local training paths are rejected by HF YAML validation)."""
    return f"""---
library_name: peft
base_model: {base_model}
tags:
- lora
- peft
- code
- {intent}
- codegen
pipeline_tag: text-generation
---

# {repo_id}

LoRA adapter for **{intent}** on [{base_model}](https://huggingface.co/{base_model}).

- Checkpoint version: `{version}`
- Task: `{intent}`

## Usage

```python
from peft import PeftModel
from transformers import AutoModelForCausalLM, AutoTokenizer

base = "{base_model}"
adapter = "{repo_id}"

tokenizer = AutoTokenizer.from_pretrained(base)
model = AutoModelForCausalLM.from_pretrained(base)
model = PeftModel.from_pretrained(model, adapter)
```

Or use the multi-adapter API in this project's `hf-deploy/` package.
"""


def _stage_adapter_dir(
    local: Path,
    *,
    intent: str,
    base_model: str,
    version: str,
    repo_id: str,
    staging_root: Path,
) -> Path:
    """Copy adapter weights and write a Hub-valid README + fixed adapter_config."""
    staged = staging_root / intent
    staged.mkdir(parents=True, exist_ok=True)

    for name in _UPLOAD_FILES:
        src = local / name
        if src.is_file():
            shutil.copy2(src, staged / name)

    config_path = staged / "adapter_config.json"
    if config_path.is_file():
        config = json.loads(config_path.read_text(encoding="utf-8"))
        # Training saved a local cache path; Hub consumers need the model id.
        if config.get("base_model_name_or_path"):
            config["base_model_name_or_path"] = base_model
        config_path.write_text(json.dumps(config, indent=2) + "\n", encoding="utf-8")

    (staged / "README.md").write_text(
        _model_card(intent, base_model, version, repo_id),
        encoding="utf-8",
    )
    return staged


def main() -> int:
    _load_env_files()

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--version", help="Override checkpoint_version from manifest")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Resolve paths and print Hub targets without uploading",
    )
    parser.add_argument(
        "--private",
        action="store_true",
        help="Create private Hub repos",
    )
    args = parser.parse_args()

    manifest = load_manifest()
    version = args.version or manifest["checkpoint_version"]
    base_model = str(manifest.get("base_model") or "Salesforce/codegen-350M-multi")
    hub = manifest.get("hub") or {}
    repos = hub.get("repos") or {}
    org = hub.get("org") or ""

    paths = resolve_version_adapters(
        manifest["checkpoints_root"],
        version,
        manifest.get("adapters"),
    )

    token = _resolve_hf_token()
    api = None
    if not args.dry_run:
        if not token:
            print(
                "ERROR: No Hugging Face token found.\n"
                "Set HF_TOKEN in hf-deploy/.env or the repo .env, or run:\n"
                "  hf auth login\n"
                "Token needs 'Write' permission: https://huggingface.co/settings/tokens",
                file=sys.stderr,
            )
            return 1
        from huggingface_hub import HfApi

        api = HfApi(token=token)

    # Dry-run can show placeholders; real upload always uses user/org namespace.
    try:
        namespace = _namespace(api, org) if api is not None else (
            (org or os.getenv("HF_ORG") or "<your-username>").strip()
            or "<your-username>"
        )
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    print(f"checkpoint_version={version}")
    print(f"base_model={base_model}")
    print(f"hub_namespace={namespace}")
    for intent in INTENTS:
        local = paths[intent]
        repo_name = repos.get(intent, f"codegen-350M-{intent}-lora")
        target = _repo_id(namespace, repo_name)
        print(f"  {intent}: {local} -> {target}")

    if args.dry_run:
        print("Dry run complete (no upload).")
        return 0

    assert api is not None
    with tempfile.TemporaryDirectory(prefix="hf-deploy-publish-") as tmp:
        staging_root = Path(tmp)
        for intent in INTENTS:
            local = paths[intent]
            repo_name = repos.get(intent, f"codegen-350M-{intent}-lora")
            target = _repo_id(namespace, repo_name)
            staged = _stage_adapter_dir(
                local,
                intent=intent,
                base_model=base_model,
                version=version,
                repo_id=target,
                staging_root=staging_root,
            )
            created = api.create_repo(
                repo_id=target,
                repo_type="model",
                exist_ok=True,
                private=args.private,
            )
            # Prefer the canonical id returned by the Hub.
            full_repo_id = getattr(created, "repo_id", None) or target
            print(f"Uploading {intent} -> {full_repo_id} ...")
            api.upload_folder(
                folder_path=str(staged),
                repo_id=full_repo_id,
                repo_type="model",
            )
            print(f"  done: https://huggingface.co/{full_repo_id}")

    print("Publish complete.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
