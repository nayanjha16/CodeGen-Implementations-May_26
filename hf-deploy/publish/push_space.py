#!/usr/bin/env python3
"""Create/update the Hugging Face Space for the multi-adapter API.

Space: care2achieve/codegen-multi-adapter

Usage (from repo root):

    PYTHONPATH=hf-deploy python hf-deploy/publish/push_space.py --dry-run
    PYTHONPATH=hf-deploy python hf-deploy/publish/push_space.py
"""

from __future__ import annotations

import argparse
import os
import shutil
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = ROOT.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from hf_deploy.config import load_manifest  # noqa: E402

_SPACE_FILES = (
    "Dockerfile",
    "requirements.txt",
)


def _load_env_files() -> None:
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


def _space_repo_id(manifest: dict) -> str:
    hub = manifest.get("hub") or {}
    org = str(hub.get("org") or os.getenv("HF_ORG") or "care2achieve").strip()
    name = str(hub.get("space_repo") or "codegen-multi-adapter").strip()
    if "/" in name:
        return name
    return f"{org}/{name}"


def _stage_space(staging: Path) -> None:
    """Assemble the Docker Space payload."""
    for name in _SPACE_FILES:
        src = ROOT / name
        if not src.is_file():
            raise FileNotFoundError(f"Missing {src}")
        shutil.copy2(src, staging / name)

    # Space-specific README + hub-default manifest
    shutil.copy2(ROOT / "space" / "README.md", staging / "README.md")
    shutil.copy2(ROOT / "space" / "manifest.yaml", staging / "manifest.yaml")

    # Python package only (no local tests / .env)
    pkg_src = ROOT / "hf_deploy"
    pkg_dst = staging / "hf_deploy"
    shutil.copytree(
        pkg_src,
        pkg_dst,
        ignore=shutil.ignore_patterns("__pycache__", "*.pyc", ".pytest_cache"),
    )


def main() -> int:
    _load_env_files()
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument(
        "--private",
        action="store_true",
        help="Create a private Space",
    )
    args = parser.parse_args()

    manifest = load_manifest()
    repo_id = _space_repo_id(manifest)
    print(f"space_repo={repo_id}")

    with tempfile.TemporaryDirectory(prefix="hf-deploy-space-") as tmp:
        staging = Path(tmp) / "space"
        staging.mkdir()
        _stage_space(staging)
        print("Staged files:")
        for path in sorted(staging.rglob("*")):
            if path.is_file():
                print(f"  {path.relative_to(staging)}")

        if args.dry_run:
            print("Dry run complete (no upload).")
            return 0

        token = _resolve_hf_token()
        if not token:
            print(
                "ERROR: No HF_TOKEN found. Set it in .env or run: hf auth login",
                file=sys.stderr,
            )
            return 1

        from huggingface_hub import HfApi
        from huggingface_hub.errors import HfHubHTTPError

        api = HfApi(token=token)
        try:
            created = api.create_repo(
                repo_id=repo_id,
                repo_type="space",
                space_sdk="docker",
                exist_ok=True,
                private=args.private,
            )
        except HfHubHTTPError as exc:
            status = getattr(exc.response, "status_code", None)
            if status == 402:
                print(
                    "ERROR: Hugging Face returned 402 Payment Required.\n"
                    "Docker/Gradio Spaces on free CPU now need Hugging Face PRO:\n"
                    "  https://huggingface.co/pro\n\n"
                    "Until then, run the API locally:\n"
                    "  export HF_DEPLOY_ADAPTER_SOURCE=hub\n"
                    "  export HF_ORG=care2achieve\n"
                    "  PYTHONPATH=hf-deploy uvicorn hf_deploy.api.app:app "
                    "--host 0.0.0.0 --port 8000\n",
                    file=sys.stderr,
                )
                return 1
            raise
        full_id = getattr(created, "repo_id", None) or repo_id
        print(f"Uploading Space -> {full_id} ...")
        api.upload_folder(
            folder_path=str(staging),
            repo_id=full_id,
            repo_type="space",
        )
        print(f"done: https://huggingface.co/spaces/{full_id}")
        print(
            "URL (after build): "
            f"https://{full_id.replace('/', '-').lower()}.hf.space"
        )
        print("OpenAI base: that URL + /v1")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
