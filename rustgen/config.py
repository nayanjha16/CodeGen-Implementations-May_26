"""Single source of truth for runtime configuration.

Switching from the mock backend to the real fine-tuned model is a config
change only: set ``backend="hf"`` (and ``adapter_path`` once a LoRA adapter
exists). Every field can also be overridden via a ``RUSTGEN_<FIELD>`` env var.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, fields

_INT_FIELDS = {"rag_k", "max_new_tokens"}
_BOOL_FIELDS = {"rag_enabled"}
_TRUTHY = {"1", "true", "yes", "on"}


@dataclass
class Config:
    backend: str = "mock"            # "mock" | "hf"
    base_model: str = "Salesforce/codegen-350M-multi"
    adapter_path: str | None = None  # e.g. "models/lora-v1" once trained
    pivot_model: str = "Qwen/Qwen2.5-Coder-1.5B-Instruct"  # drafts Python for English→Rust
    rag_enabled: bool = False
    rag_backend: str = "mock"        # "mock" | "tfidf"
    rag_corpus_path: str = "data/rust_corpus.jsonl"
    rag_k: int = 3
    max_new_tokens: int = 256
    device: str = "auto"

    @classmethod
    def from_env(cls) -> Config:
        """Defaults, overridden by RUSTGEN_* env vars (e.g. RUSTGEN_BACKEND=hf)."""
        kwargs = {}
        for f in fields(cls):
            raw = os.environ.get(f"RUSTGEN_{f.name.upper()}")
            if raw is None or raw == "":
                continue
            if f.name in _INT_FIELDS:
                kwargs[f.name] = int(raw)
            elif f.name in _BOOL_FIELDS:
                kwargs[f.name] = raw.lower() in _TRUTHY
            else:
                kwargs[f.name] = raw
        return cls(**kwargs)
