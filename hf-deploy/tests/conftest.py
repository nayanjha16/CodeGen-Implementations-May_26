"""Pytest path bootstrap for hf-deploy package."""

from __future__ import annotations

import sys
from pathlib import Path

HF_DEPLOY_ROOT = Path(__file__).resolve().parents[1]
if str(HF_DEPLOY_ROOT) not in sys.path:
    sys.path.insert(0, str(HF_DEPLOY_ROOT))
