"""Shared Hugging Face auth helpers for deploy scripts."""

from __future__ import annotations

import sys


def require_hf_auth() -> str:
    """Return the authenticated HF username or exit with instructions."""
    try:
        from huggingface_hub import HfApi
        from huggingface_hub.errors import LocalTokenNotFoundError
    except ImportError:
        print("Install huggingface_hub: .venv/bin/pip install huggingface_hub", file=sys.stderr)
        raise SystemExit(1)

    try:
        whoami = HfApi().whoami()
    except LocalTokenNotFoundError:
        print(
            "Hugging Face login required.\n\n"
            "  .venv/bin/huggingface-cli login\n\n"
            "Or set HF_TOKEN to a write token from https://huggingface.co/settings/tokens\n"
            "Then rerun deploy.",
            file=sys.stderr,
        )
        raise SystemExit(1)

    name = whoami.get("name") or whoami.get("fullname") or "unknown"
    return str(name)
