"""Code generation wrapper for the HF Space (loads model from MODEL_ID env var)."""

from __future__ import annotations

import os
import re
from typing import Any, cast

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

DEFAULT_MODEL_ID = os.environ.get("MODEL_ID", "Saikrishna2511/qwen-multitask")


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
        response_type: str = "code",
    ) -> str:
        max_new_tokens = max_new_tokens or self.max_new_tokens
        temperature = self.temperature if temperature is None else temperature
        top_p = self.top_p if top_p is None else top_p
        do_sample = temperature > 0

        inputs = self.tokenizer(prompt, return_tensors="pt", truncation=True, max_length=1024)
        inputs = {k: v.to(self.device) for k, v in inputs.items()}

        with torch.no_grad():
            outputs = self.model.generate(
                **inputs,
                max_new_tokens=max_new_tokens,
                temperature=temperature,
                top_p=top_p,
                do_sample=do_sample,
                pad_token_id=self.tokenizer.pad_token_id,
                eos_token_id=self.tokenizer.eos_token_id,
            )

        generated = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        if generated.startswith(prompt):
            generated = generated[len(prompt):]
        generated = generated.strip()

        if response_type == "doc":
            return self._extract_documentation(generated)
        return self._extract_code(generated)

    @staticmethod
    def _extract_documentation(text: str) -> str:
        closing_fence = re.search(r"```", text)
        if closing_fence:
            return text[: closing_fence.start()].strip()
        return text.strip()

    @staticmethod
    def _extract_code(text: str) -> str:
        closing = re.search(r"```", text)
        if closing and not re.match(r"\s*```", text):
            return text[: closing.start()].strip()

        py_match = re.search(r"```python\s*(.*?)```", text, re.DOTALL)
        if py_match:
            return py_match.group(1).strip()

        generic_match = re.search(r"```\s*(.*?)```", text, re.DOTALL)
        if generic_match:
            return generic_match.group(1).strip()

        return text.strip()
