"""LangChain LLM wrappers around the fine-tuned codegen model and judge."""

from __future__ import annotations

import inspect
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
DEFAULT_PLANNER_MODEL = "Qwen/Qwen2.5-1.5B-Instruct"
DEFAULT_ASK_MODEL = "Qwen/Qwen2.5-1.5B-Instruct"

_codegen: Any = None
_judge: Any = None
_planner: Any = None
_ask: Any = None


def set_codegen_generator(generator: Any) -> None:
    """Inject a pre-loaded CodeGenerator (e.g. from FastAPI lifespan)."""
    global _codegen
    _codegen = generator


def set_judge_generator(generator: Any) -> None:
    """Inject a pre-loaded judge generator (tests / shared process)."""
    global _judge
    _judge = generator


def set_planner_generator(generator: Any) -> None:
    """Inject a pre-loaded planner generator (tests)."""
    global _planner
    _planner = generator


def set_ask_generator(generator: Any) -> None:
    """Inject a pre-loaded Ask Q&A generator (tests / shared process)."""
    global _ask
    _ask = generator


def get_codegen_generator():
    """Lazy-load the fine-tuned multitask CodeGenerator."""
    global _codegen
    if _codegen is None:
        from generator import load_generator

        _codegen = load_generator("java2py")
    return _codegen


def _load_side_model(env_key: str, default_id: str, max_new_tokens: int) -> Any:
    model_id = os.environ.get(env_key, default_id)
    if model_id in ("ft", "same", "codegen"):
        return get_codegen_generator()
    from generator import CodeGenerator

    return CodeGenerator(
        model_path=model_id, temperature=0.0, max_new_tokens=max_new_tokens
    )


def get_judge_generator():
    """Lazy-load the separate Instruct judge model."""
    global _judge
    if _judge is None:
        _judge = _load_side_model("JUDGE_MODEL_ID", DEFAULT_JUDGE_MODEL, 64)
    return _judge


def get_planner_generator():
    """Lazy-load the Ask query planner model."""
    global _planner
    if _planner is None:
        _planner = _load_side_model(
            "ASK_PLANNER_MODEL_ID", DEFAULT_PLANNER_MODEL, 128
        )
    return _planner


def get_ask_generator():
    """Lazy-load (and cache) the model used for Ask Agent Q&A answers."""
    global _ask
    if _ask is None:
        ask_id = os.environ.get("ASK_MODEL_ID", DEFAULT_ASK_MODEL)
        if ask_id in ("ft", "same", "codegen"):
            _ask = get_codegen_generator()
        else:
            from generator import CodeGenerator

            _ask = CodeGenerator(
                model_path=ask_id, temperature=0.0, max_new_tokens=512
            )
    return _ask


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


def planner_generate(prompt: str) -> str:
    gen = get_planner_generator()
    return gen.generate(
        prompt,
        temperature=0.0,
        max_new_tokens=128,
        response_type="doc",
    )


def _generate_with_supported_kwargs(gen: Any, prompt: str, **kwargs: Any) -> str:
    """Call generate() with only kwargs supported by the injected generator."""
    supported = inspect.signature(gen.generate).parameters
    filtered = {key: value for key, value in kwargs.items() if key in supported}
    return gen.generate(prompt, **filtered)


def fix_generate(
    prompt: str,
    *,
    attempts: int = 0,
    temperature: float | None = None,
    max_new_tokens: int = 512,
) -> str:
    """Generate Python fixes; escalate to Instruct model on later retries."""
    if attempts >= 2:
        gen = get_ask_generator()
        return _generate_with_supported_kwargs(
            gen,
            prompt,
            temperature=0.0,
            max_new_tokens=max_new_tokens,
            repetition_penalty=1.15,
            response_type="code",
        )
    temp = temperature if temperature is not None else max(0.05, 0.3 - 0.05 * attempts)
    return codegen_generate(prompt, temperature=temp, max_new_tokens=max_new_tokens)


def ask_generate(
    prompt: str,
    *,
    max_new_tokens: int = 256,
) -> str:
    """Generate Ask Agent Q&A answers with conservative decoding."""
    gen = get_ask_generator()
    return _generate_with_supported_kwargs(
        gen,
        prompt,
        temperature=0.0,
        max_new_tokens=max_new_tokens,
        repetition_penalty=1.15,
        response_type="doc",
    )


# LangChain Runnables for graph nodes / tooling
codegen_runnable = RunnableLambda(lambda prompt: codegen_generate(str(prompt)))
judge_runnable = RunnableLambda(lambda prompt: judge_generate(str(prompt)))


@lru_cache(maxsize=1)
def get_codegen_runnable():
    return codegen_runnable


@lru_cache(maxsize=1)
def get_judge_runnable():
    return judge_runnable
