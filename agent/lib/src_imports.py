"""Import selected src modules without triggering package __init__ circular imports."""

from __future__ import annotations

import importlib.util
from functools import lru_cache
from pathlib import Path
from types import ModuleType

_REPO_ROOT = Path(__file__).resolve().parents[2]


def _load_module(name: str, relative_path: str) -> ModuleType:
    path = _REPO_ROOT / relative_path
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Cannot load module from {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@lru_cache(maxsize=1)
def documentation_prompt_builder_class():
    """Return DocumentationPromptBuilder without importing src.documentation.__init__."""
    module = _load_module(
        "agent_src_documentation_prompt_builder",
        "src/documentation/prompt_builder.py",
    )
    return module.DocumentationPromptBuilder
