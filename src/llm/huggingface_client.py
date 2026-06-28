"""Local Hugging Face chat client for judge and codegen fallbacks."""

from __future__ import annotations

import logging
from typing import Any

from src.models.model_loader import ensure_model_cached, is_model_cached
from src.utils.device import resolve_device
from src.utils.paths import get_model_cache_dir

logger = logging.getLogger("codegen")

DEFAULT_MAX_NEW_TOKENS = 512
DEFAULT_TEMPERATURE = 0.1


class HuggingFaceClient:
    """Run chat-style prompts against locally loaded Hugging Face causal LMs."""

    def __init__(self, device: str = "auto", max_new_tokens: int = DEFAULT_MAX_NEW_TOKENS):
        self.device = resolve_device(device)
        self.max_new_tokens = max_new_tokens
        self._models: dict[str, tuple[Any, Any]] = {}

    def _load_model(self, model_name: str) -> tuple[Any, Any]:
        if model_name in self._models:
            return self._models[model_name]

        from transformers import AutoModelForCausalLM, AutoTokenizer
        from transformers.utils import logging as transformers_logging

        transformers_logging.set_verbosity_error()

        cache_dir = ensure_model_cached(model_name)
        load_kwargs = {"local_files_only": True} if is_model_cached(cache_dir) else {}
        tokenizer = AutoTokenizer.from_pretrained(cache_dir, **load_kwargs)
        if tokenizer.pad_token_id is None:
            tokenizer.pad_token = tokenizer.eos_token

        model = AutoModelForCausalLM.from_pretrained(cache_dir, **load_kwargs)
        model.to(self.device)
        model.eval()

        logger.info("Loaded Hugging Face chat model %s on %s", model_name, self.device)
        self._models[model_name] = (tokenizer, model)
        return tokenizer, model

    @staticmethod
    def _prepare_messages(
        messages: list[dict[str, str]],
        *,
        format_json: bool,
    ) -> list[dict[str, str]]:
        prepared = [dict(message) for message in messages]
        if not format_json:
            return prepared

        json_instruction = "Respond with valid JSON only. Do not include markdown fences."
        if prepared and prepared[-1].get("role") == "user":
            content = prepared[-1].get("content", "").rstrip()
            prepared[-1]["content"] = f"{content}\n\n{json_instruction}"
        else:
            prepared.append({"role": "user", "content": json_instruction})
        return prepared

    def _format_prompt(self, tokenizer: Any, messages: list[dict[str, str]]) -> str:
        if hasattr(tokenizer, "apply_chat_template") and tokenizer.chat_template:
            return tokenizer.apply_chat_template(
                messages,
                tokenize=False,
                add_generation_prompt=True,
            )

        parts: list[str] = []
        for message in messages:
            role = message.get("role", "user")
            content = message.get("content", "")
            parts.append(f"{role}: {content}")
        parts.append("assistant:")
        return "\n".join(parts)

    def chat(
        self,
        model: str,
        messages: list[dict[str, str]],
        *,
        format_json: bool = False,
        think: bool | None = None,
    ) -> str:
        del think  # Ollama-only parameter; ignored for Hugging Face.

        tokenizer, llm = self._load_model(model)
        prepared = self._prepare_messages(messages, format_json=format_json)
        prompt = self._format_prompt(tokenizer, prepared)

        import torch

        inputs = tokenizer(
            prompt,
            return_tensors="pt",
            truncation=True,
            max_length=getattr(tokenizer, "model_max_length", 8192),
        ).to(self.device)
        input_length = inputs["input_ids"].shape[1]

        gen_kwargs: dict[str, Any] = {
            "max_new_tokens": self.max_new_tokens,
            "pad_token_id": tokenizer.eos_token_id,
            "do_sample": False,
        }

        try:
            with torch.no_grad():
                outputs = llm.generate(**inputs, **gen_kwargs)
        except RuntimeError as exc:
            cache_dir = get_model_cache_dir(model)
            raise RuntimeError(
                f"Hugging Face chat failed for model {model!r} at {cache_dir}: {exc}"
            ) from exc

        new_tokens = outputs[0][input_length:]
        return tokenizer.decode(new_tokens, skip_special_tokens=True).strip()
