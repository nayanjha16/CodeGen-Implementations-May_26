"""Standalone GenerationConfig dataclass.

Deliberately kept free of any torch/transformers import so that task modules
(`codegen_rag.tasks.*`) can be imported and unit-tested without a GPU runtime
or heavy ML dependencies installed — only `codegen_wrapper.py` itself needs
torch, and only once a real model is actually instantiated.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class GenerationConfig:
    max_new_tokens: int = 256
    temperature: float = 0.2
    top_p: float = 0.95
    do_sample: bool = True
    num_return_sequences: int = 1
    stop_sequences: list[str] = field(default_factory=list)
