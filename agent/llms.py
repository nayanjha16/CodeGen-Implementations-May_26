"""LangChain LLM wrappers around the fine-tuned codegen model and judge."""

from __future__ import annotations

import os
import sys
from functools import lru_cache
from pathlib import Path
from typing import Any

from langchain_core.runnables import RunnableLambda

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(PROJECT_ROOT / "inference"))

DEFAULT_JUDGE_MODEL = os.environ.get("JUDGE_MODEL_ID", "Qwen/Qwen2.5-1.5B-Instruct")

_codegen: Any = None
_judge: Any = None


def set_codegen_generator(generator: Any) -> None:
    """Inject a pre-loaded CodeGenerator (e.g. from FastAPI lifespan)."""
    global _codegen
    _codegen = generator


def set_judge_generator(generator: Any) -> None:
    """Inject a pre-loaded judge generator (tests / shared process)."""
    global _judge
    _judge = generator


def get_codegen_generator():
    """Lazy-load the fine-tuned multitask CodeGenerator."""
    global _codegen
    if _codegen is None:
        from generator import load_generator

        _codegen = load_generator("java2py")
    return _codegen


def get_judge_generator():
    """Lazy-load the separate Instruct judge model."""
    global _judge
    if _judge is None:
        # Allow reuse of FT model when JUDGE_MODEL_ID=ft or same as MODEL_ID
        judge_id = os.environ.get("JUDGE_MODEL_ID", DEFAULT_JUDGE_MODEL)
        if judge_id in ("ft", "same", "codegen"):
            _judge = get_codegen_generator()
        else:
            from generator import CodeGenerator

            _judge = CodeGenerator(model_path=judge_id, temperature=0.0, max_new_tokens=64)
    return _judge


def codegen_generate(
    prompt: str,
    *,
    temperature: float | None = None,
    max_new_tokens: int | None = None,
    response_type: str = "code",
) -> str:
    gen = get_codegen_generator()
    return gen.generate(
        prompt,
        temperature=temperature,
        max_new_tokens=max_new_tokens,
        response_type=response_type,
    )


def judge_generate(prompt: str) -> str:
    gen = get_judge_generator()
    # Judge should return plain text, not extracted code fences only
    raw = gen.generate(prompt, temperature=0.0, max_new_tokens=64, response_type="doc")
    return raw


# LangChain Runnables for graph nodes / tooling
codegen_runnable = RunnableLambda(lambda prompt: codegen_generate(str(prompt)))
judge_runnable = RunnableLambda(lambda prompt: judge_generate(str(prompt)))


@lru_cache(maxsize=1)
def get_codegen_runnable():
    return codegen_runnable


@lru_cache(maxsize=1)
def get_judge_runnable():
    return judge_runnable
