"""Publish LoRA adapters to the Hugging Face Hub.

Uploads ``models/checkpoints/<version>/<task>/`` to
``<org>/codegen-350M-<task>-lora`` for each task, with a Hub-valid model card.

Examples (run from the repo root):

    # Preview what would be pushed (no upload)
    PYTHONPATH=fastapi-deploy python fastapi-deploy/publish/push_adapters.py --dry-run

    # Publish version v3 to the default org (codegenstudio)
    PYTHONPATH=fastapi-deploy python fastapi-deploy/publish/push_adapters.py --version v3

Windows PowerShell:

    $env:PYTHONPATH = "fastapi-deploy"
    python fastapi-deploy/publish/push_adapters.py --version v3

Auth: run ``hf auth login`` once, or pass ``--token`` / set ``HF_TOKEN``.
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

from codegen_api import INTENTS
from codegen_api.adapters.resolve import resolve_best_adapter
from codegen_api.config import load_manifest

MODEL_CARD = """---
base_model: Salesforce/codegen-350M-multi
library_name: peft
pipeline_tag: text-generation
tags:
  - lora
  - peft
  - {task}
---

# {org}/codegen-350M-{task}-lora

LoRA adapter for {task} on Salesforce/codegen-350M-multi.

- Checkpoint version: `{version}`
- Task: `{task}`

## Usage

```python
from peft import PeftModel
from transformers import AutoModelForCausalLM, AutoTokenizer

base = "Salesforce/codegen-350M-multi"
adapter = "{org}/codegen-350M-{task}-lora"

tokenizer = AutoTokenizer.from_pretrained(base)
model = AutoModelForCausalLM.from_pretrained(base)
model = PeftModel.from_pretrained(model, adapter)
```

Or use the multi-adapter API in this project's `fastapi-deploy/` package.
"""


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Publish LoRA adapters to the Hub.")
    parser.add_argument(
        "--version",
        default=None,
        help="Checkpoint version under models/checkpoints/ (default: manifest value).",
    )
    parser.add_argument(
        "--org",
        default=None,
        help="Hub org/namespace (default: HF_ORG env or manifest hub.org).",
    )
    parser.add_argument(
        "--token",
        default=os.getenv("HF_TOKEN"),
        help="Hugging Face token (default: HF_TOKEN env or cached `hf auth login`).",
    )
    parser.add_argument(
        "--private",
        action="store_true",
        help="Create/keep the repos private (default: public).",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print what would be uploaded without contacting the Hub.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    manifest = load_manifest()
    version = args.version or manifest["checkpoint_version"]
    org = args.org or manifest.get("hub", {}).get("org") or os.getenv("HF_ORG")
    if not org:
        print("ERROR: no org. Pass --org or set HF_ORG / hub.org in manifest.yaml.")
        return 2

    checkpoints_root = manifest["checkpoints_root"]
    adapter_names = manifest.get("adapters") or {}

    print(f"Publishing version '{version}' to org '{org}' "
          f"({'DRY RUN' if args.dry_run else 'LIVE'})")

    plan: list[tuple[str, Path, str]] = []
    for intent in INTENTS:
        folder = adapter_names.get(intent, intent)
        task_dir = Path(checkpoints_root) / version / folder
        try:
            adapter_dir = resolve_best_adapter(task_dir)
        except FileNotFoundError as exc:
            print(f"  ERROR: {exc}")
            return 1
        repo_id = f"{org}/codegen-350M-{intent}-lora"
        plan.append((intent, adapter_dir, repo_id))
        print(f"  {intent:10s}: {adapter_dir}  ->  {repo_id}")

    if args.dry_run:
        print("Dry run complete. No files uploaded.")
        return 0

    from huggingface_hub import HfApi

    api = HfApi(token=args.token)
    for intent, adapter_dir, repo_id in plan:
        print(f"\nUploading {intent} -> {repo_id}")
        api.create_repo(
            repo_id=repo_id,
            repo_type="model",
            private=args.private,
            exist_ok=True,
        )
        card = MODEL_CARD.format(org=org, task=intent, version=version)
        (adapter_dir / "README.md").write_text(card, encoding="utf-8")
        api.upload_folder(
            repo_id=repo_id,
            folder_path=str(adapter_dir),
            repo_type="model",
            commit_message=f"Publish {intent} adapter ({version})",
        )
        print(f"  done: https://huggingface.co/{repo_id}")

    print("\nAll adapters published.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
