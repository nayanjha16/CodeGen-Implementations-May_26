"""Judge inference backends: Ollama when available, otherwise Hugging Face."""

from __future__ import annotations

import logging
from typing import Any, Protocol

from src.llm.ollama_client import OllamaClient
from src.models.model_loader import ensure_model_cached, is_model_cached
from src.utils.config import get_judge_hf_model
from src.utils.device import resolve_device
from src.utils.paths import get_model_cache_dir

logger = logging.getLogger("codegen")

OLLAMA_TO_HF_JUDGE_MODEL: dict[str, str] = {
    "gemma3:4b": "google/gemma-3-4b-it",
    "gemma3:4b-it": "google/gemma-3-4b-it",
    "gemma3": "google/gemma-3-4b-it",
    "qwen3:4b": "Qwen/Qwen3-4B-Instruct-2507",
    "qwen3": "Qwen/Qwen3-4B-Instruct-2507",
    "qwen2.5:3b": "Qwen/Qwen2.5-3B-Instruct",
    "qwen2.5-coder:3b": "Qwen/Qwen2.5-Coder-3B-Instruct",
}


class JudgeBackend(Protocol):
    backend_name: str
    model_label: str

    def generate(self, prompt: str, *, format_json: bool = False) -> str:
        """Generate a judge response for the given prompt."""


def resolve_hf_judge_model(
    ollama_model: str,
    explicit_hf_model: str | None = None,
) -> str:
    """Map an Ollama judge tag to a Hugging Face model id."""
    if explicit_hf_model and explicit_hf_model.strip():
        return explicit_hf_model.strip()

    candidate = ollama_model.strip()
    if "/" in candidate:
        return candidate

    lookup = candidate.lower()
    if lookup in OLLAMA_TO_HF_JUDGE_MODEL:
        return OLLAMA_TO_HF_JUDGE_MODEL[lookup]

    base = lookup.split(":", 1)[0]
    if base in OLLAMA_TO_HF_JUDGE_MODEL:
        return OLLAMA_TO_HF_JUDGE_MODEL[base]

    supported = ", ".join(sorted(OLLAMA_TO_HF_JUDGE_MODEL))
    raise ValueError(
        f"No Hugging Face fallback mapping for Ollama judge model {ollama_model!r}. "
        f"Set JUDGE_HF_MODEL in .env to a Hugging Face model id, or use one of: "
        f"{supported}."
    )


class OllamaJudgeBackend:
    """Run judge prompts through a local Ollama model."""

    backend_name = "ollama"

    def __init__(
        self,
        model_name: str,
        client: OllamaClient | None = None,
    ):
        self.model_name = model_name
        self.model_label = model_name
        self._client = client or OllamaClient()

    def generate(self, prompt: str, *, format_json: bool = False) -> str:
        messages = [{"role": "user", "content": prompt}]
        return self._client.chat(
            self.model_name,
            messages,
            format_json=format_json,
            think=False,
        )


class HfJudgeBackend:
    """Run judge prompts through a cached Hugging Face causal LM."""

    backend_name = "huggingface"

    def __init__(
        self,
        hf_model_name: str,
        *,
        device: str = "auto",
        max_new_tokens: int = 512,
    ):
        self.hf_model_name = hf_model_name
        self.model_label = hf_model_name
        self.device = resolve_device(device)
        self.max_new_tokens = max_new_tokens
        self._model: Any = None
        self._tokenizer: Any = None

    def _load(self) -> None:
        if self._model is not None and self._tokenizer is not None:
            return

        import torch
        from transformers import AutoModelForCausalLM, AutoTokenizer
        from transformers.utils import logging as transformers_logging

        transformers_logging.set_verbosity_error()

        cache_dir = ensure_model_cached(self.hf_model_name)
        load_kwargs = (
            {"local_files_only": True} if is_model_cached(cache_dir) else {}
        )
        logger.info(
            "Loading Hugging Face judge model %s from %s on %s",
            self.hf_model_name,
            cache_dir,
            self.device,
        )
        self._tokenizer = AutoTokenizer.from_pretrained(cache_dir, **load_kwargs)
        if self._tokenizer.pad_token_id is None:
            self._tokenizer.pad_token = self._tokenizer.eos_token

        dtype = torch.float16 if self.device == "cuda" else torch.float32
        self._model = AutoModelForCausalLM.from_pretrained(
            cache_dir,
            torch_dtype=dtype,
            low_cpu_mem_usage=True,
            **load_kwargs,
        )
        self._model.to(self.device)
        self._model.eval()

    def generate(self, prompt: str, *, format_json: bool = False) -> str:
        import torch

        self._load()
        assert self._model is not None
        assert self._tokenizer is not None

        messages = [{"role": "user", "content": prompt}]
        if hasattr(self._tokenizer, "apply_chat_template"):
            rendered = self._tokenizer.apply_chat_template(
                messages,
                tokenize=False,
                add_generation_prompt=True,
            )
        else:
            rendered = prompt

        inputs = self._tokenizer(
            rendered,
            return_tensors="pt",
            truncation=True,
            max_length=4096,
        ).to(self.device)
        input_length = inputs["input_ids"].shape[1]

        gen_kwargs: dict[str, Any] = {
            "max_new_tokens": self.max_new_tokens,
            "do_sample": False,
            "pad_token_id": self._tokenizer.eos_token_id,
        }

        with torch.no_grad():
            outputs = self._model.generate(**inputs, **gen_kwargs)

        new_tokens = outputs[0][input_length:]
        return self._tokenizer.decode(new_tokens, skip_special_tokens=True).strip()


def create_judge_backend(
    ollama_model: str,
    *,
    ollama_client: OllamaClient | None = None,
    hf_model: str | None = None,
    device: str = "auto",
) -> JudgeBackend:
    """Prefer Ollama when the configured judge model is available, else Hugging Face."""
    client = ollama_client or OllamaClient()
    explicit_hf = hf_model or get_judge_hf_model()

    if client.is_available() and client.has_model(ollama_model):
        logger.info("Using Ollama judge model %s", ollama_model)
        print(f"Judge backend: ollama ({ollama_model})")
        return OllamaJudgeBackend(ollama_model, client=client)

    hf_model_name = resolve_hf_judge_model(ollama_model, explicit_hf)
    if client.is_available():
        logger.warning(
            "Ollama is running but model %s is not available; "
            "falling back to Hugging Face judge %s",
            ollama_model,
            hf_model_name,
        )
        print(
            f"Judge backend: huggingface ({hf_model_name}) "
            f"[Ollama model {ollama_model!r} not found]"
        )
    else:
        logger.warning(
            "Ollama is not available at %s; falling back to Hugging Face judge %s",
            client.base_url,
            hf_model_name,
        )
        print(
            f"Judge backend: huggingface ({hf_model_name}) "
            f"[Ollama unavailable at {client.base_url}]"
        )

    cache_dir = get_model_cache_dir(hf_model_name)
    if not is_model_cached(cache_dir):
        print(f"Downloading Hugging Face judge model {hf_model_name} to {cache_dir} ...")

    return HfJudgeBackend(hf_model_name, device=device)
