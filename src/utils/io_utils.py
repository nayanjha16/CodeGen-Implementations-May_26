"""Hugging Face token retrieval and JSON persistence helpers."""
import json
import os
from getpass import getpass
from pathlib import Path
from typing import Optional

from utils.logger import logger


def get_hf_token() -> Optional[str]:
    """Return a HF token from the first available source: Kaggle secret,
    environment variable, Colab userdata, or an interactive prompt."""
    try:
        from kaggle_secrets import UserSecretsClient
        return UserSecretsClient().get_secret("HF_WRITE_TOKEN")
    except Exception:
        pass

    token = os.environ.get("HF_WRITE_TOKEN") or os.environ.get("HF_TOKEN")
    if token:
        return token

    try:
        from google.colab import userdata
        return userdata.get("HF_WRITE_TOKEN")
    except Exception:
        pass

    return getpass("Enter your Hugging Face token: ")


def ensure_dir(path: str) -> str:
    Path(path).mkdir(parents=True, exist_ok=True)
    return path


def save_json(data: dict, path: str) -> None:
    ensure_dir(str(Path(path).parent))
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(data, fh, indent=2, default=str)
    logger.info("Saved JSON to %s", path)


def load_json(path: str) -> dict:
    with open(path, "r", encoding="utf-8") as fh:
        return json.load(fh)
