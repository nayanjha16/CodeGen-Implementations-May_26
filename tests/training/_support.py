"""Shared helpers for training integration tests."""

from __future__ import annotations

import os
from typing import Any

TRAINING_TEST_MODEL = "Salesforce/codegen-350M-multi"


def load_training_test_config() -> dict[str, Any]:
    """Load config pinned to the project base model for training tests."""
    from src.utils.config import load_config

    os.environ["MODEL_NAME"] = TRAINING_TEST_MODEL
    return load_config()
