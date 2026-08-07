"""Code generation wrapper for the HF Space (loads model from MODEL_ID env var)."""

from __future__ import annotations

import ast
import os
import re
import sys
from pathlib import Path
from typing import Any, cast

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

_SPACE_DIR = Path(__file__).resolve().parent
_repo_root = _SPACE_DIR.parent.parent
_PROJECT_ROOT = _repo_root if (_repo_root / "agent").is_dir() else _SPACE_DIR
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

from utils.text_sanitize import truncate_roleplay_continuation

# Same FT weights as local models/qwen_multitask/merged (Space sets MODEL_ID).
HF_FT_MODEL = "Saikrishna2511/qwen-multitask"
DEFAULT_MODEL_ID = os.environ.get("MODEL_ID", HF_FT_MODEL)


def _get_best_device() -> str:
    if torch.cuda.is_available():
        return "cuda"
    if hasattr(torch.backends, "mps") and torch.backends.mps.is_available():
        return "mps"
    return "cpu"


def _get_inference_dtype(device: str) -> torch.dtype:
    if device == "cuda":
        return torch.float16
    if device == "mps":
        return torch.bfloat16
    return torch.float32


def _is_probably_python(text: str) -> bool:
    """Distinguish real Python from prose/markdown left in the model output."""
    try:
        tree = ast.parse(text)
    except SyntaxError:
        return False
    body = getattr(tree, "body", [])
    if not body:
        return False
    # A lone bare name/literal ("Sure", "python") is prose, not code.
    if len(body) == 1 and isinstance(body[0], ast.Expr):
        if isinstance(body[0].value, (ast.Name, ast.Constant)):
            return False
    return True


def _strip_language_tag(code: str) -> str:
    """Drop a stray leading ``python``/``py``/``java`` line echoed by the model."""
    parts = code.split("\n", 1)
    if len(parts) > 1 and parts[0].strip().lower() in ("python", "py", "java"):
        return parts[1].strip()
    return code


class CodeGenerator:
    def __init__(
        self,
        model_path: str | None = None,
        max_new_tokens: int = 512,
        temperature: float = 0.2,
        top_p: float = 0.95,
    ):
        self.model_path = model_path or DEFAULT_MODEL_ID
        self.device = _get_best_device()
        self.max_new_tokens = max_new_tokens
        self.temperature = temperature
        self.top_p = top_p
        dtype = _get_inference_dtype(self.device)

        print(f"Loading model {self.model_path} on {self.device} (dtype={dtype})")
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_path, trust_remote_code=True)
        if self.tokenizer.pad_token is None:
            self.tokenizer.pad_token = self.tokenizer.eos_token

        self.model: Any = cast(
            Any,
            AutoModelForCausalLM.from_pretrained(
                self.model_path,
                trust_remote_code=True,
                torch_dtype=dtype,
            ),
        )
        self.model.to(self.device)
        self.model.eval()

    def generate(
        self,
        prompt: str,
        max_new_tokens: int | None = None,
        temperature: float | None = None,
        top_p: float | None = None,
        do_sample: bool | None = None,
        repetition_penalty: float | None = None,
        response_type: str = "code",
    ) -> str:
        max_new_tokens = max_new_tokens or self.max_new_tokens
        temperature = self.temperature if temperature is None else temperature
        top_p = self.top_p if top_p is None else top_p
        do_sample = (temperature > 0) if do_sample is None else do_sample

        max_input_length = 3072 if response_type == "doc" else 1024
        inputs = self.tokenizer(
            prompt, return_tensors="pt", truncation=True, max_length=max_input_length
        )
        inputs = {k: v.to(self.device) for k, v in inputs.items()}
        input_len = inputs["input_ids"].shape[1]

        with torch.no_grad():
            outputs = self.model.generate(
                **inputs,
                max_new_tokens=max_new_tokens,
                temperature=temperature,
                top_p=top_p,
                do_sample=do_sample,
                repetition_penalty=repetition_penalty or 1.0,
                pad_token_id=self.tokenizer.pad_token_id,
                eos_token_id=self.tokenizer.eos_token_id,
            )

        generated = self.tokenizer.decode(
            outputs[0][input_len:], skip_special_tokens=True
        ).strip()

        if response_type == "doc":
            return self._extract_documentation(generated)
        return self._extract_code(generated)

    @staticmethod
    def _extract_documentation(text: str) -> str:
        """Extract plain documentation (Code2Doc / folder Q&A)."""
        raw = truncate_roleplay_continuation(text)
        if not raw:
            return ""
        # Drop a trailing code fence if the model starts one after the answer.
        closing_fence = re.search(r"\n```", raw)
        if closing_fence:
            return raw[: closing_fence.start()].strip()
        return raw

    @staticmethod
    def _extract_code(text: str) -> str:
        """Extract generated Python, tolerating prose and unclosed fences.

        The prompts end with an OPEN ```python fence, so the continuation
        normally starts with raw code and stops at a closing fence. Leading
        prose, missing closing fences and stray language tags are all handled so
        leftover markdown never reaches the AST/sandbox stages.
        """
        raw = (text or "").replace("\r\n", "\n").replace("\r", "\n").strip()
        if not raw:
            return ""

        first = raw.find("```")

        # Continuation of an already-open fence: code precedes the first
        # (closing) fence. Trust that prefix only when it really is Python.
        if first > 0:
            prefix = raw[:first].strip()
            if prefix and _is_probably_python(prefix):
                return _strip_language_tag(prefix)

        # A complete ```lang ... ``` block, skipping any leading prose.
        block = re.search(r"```[ \t]*\w*[ \t]*\n(.*?)```", raw, re.DOTALL)
        if block:
            return _strip_language_tag(block.group(1).strip())

        # An unclosed opening fence: drop the fence line, keep what follows.
        opening = re.search(r"```[ \t]*\w*[ \t]*\n", raw)
        if opening:
            return _strip_language_tag(raw[opening.end():].split("```")[0].strip())

        # Fence present but nothing usable after it.
        if first > 0:
            return _strip_language_tag(raw[:first].strip())
        if first == 0:
            return _strip_language_tag(raw.lstrip("`").strip())

        return _strip_language_tag(raw)
