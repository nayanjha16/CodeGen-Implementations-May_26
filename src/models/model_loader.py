"""Modular CodeGen model loading with local caching and GPU/CPU support."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

from src.utils.config import get_model_name, load_config
from src.utils.device import resolve_device
from src.utils.paths import (
    ensure_storage_dirs,
    get_checkpoint_path,
    get_model_cache_dir,
)

logger = logging.getLogger("codegen")


def is_seq2seq_model(model_name: str) -> bool:
    """Return True for encoder-decoder models such as T5."""
    lowered = model_name.lower()
    return any(tag in lowered for tag in ("t5", "bart", "pegasus", "mbart"))


def is_model_cached(path: Path) -> bool:
    """Return True when a complete HuggingFace model snapshot exists locally."""
    if not (path / "config.json").exists() or not (path / ".downloaded").exists():
        return False
    weight_files = list(path.glob("*.safetensors")) + list(path.glob("pytorch_model*.bin"))
    return bool(weight_files)


def ensure_model_cached(
    model_name: str,
    local_dir: Path | None = None,
    force: bool = False,
    *,
    causal: bool = True,
) -> Path:
    """Download and cache a HuggingFace model locally if not already present."""
    ensure_storage_dirs()
    cache_dir = local_dir or get_model_cache_dir(model_name)

    if not force and is_model_cached(cache_dir):
        print(f"Using cached model: {cache_dir}")
        logger.info("Using cached model at %s", cache_dir)
        return cache_dir

    from transformers import AutoModel, AutoModelForCausalLM, AutoModelForSeq2SeqLM, AutoTokenizer

    if causal:
        if is_seq2seq_model(model_name):
            model_cls = AutoModelForSeq2SeqLM
        else:
            model_cls = AutoModelForCausalLM
    else:
        model_cls = AutoModel
    cache_dir.mkdir(parents=True, exist_ok=True)
    print(f"Downloading model {model_name} to {cache_dir} ...")
    logger.info("Downloading model %s to %s", model_name, cache_dir)

    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = model_cls.from_pretrained(model_name)
    tokenizer.save_pretrained(cache_dir)
    model.save_pretrained(cache_dir)
    (cache_dir / ".downloaded").touch()
    return cache_dir


def resolve_model_path(config: dict[str, Any] | None = None) -> Path:
    """Resolve local model path: checkpoint if configured, otherwise cached base model."""
    config = config or load_config()
    model_cfg = config.get("model", {})

    checkpoint = model_cfg.get("checkpoint") or None
    if checkpoint:
        checkpoint_path = get_checkpoint_path(checkpoint)
        if checkpoint_path.exists() and (checkpoint_path / "config.json").exists():
            logger.info("Using checkpoint at %s", checkpoint_path)
            return checkpoint_path
        raise FileNotFoundError(
            f"Checkpoint '{checkpoint}' not found under {get_checkpoint_path('')}"
        )

    model_name = get_model_name(config)
    return ensure_model_cached(model_name)


_tokenizer_cache: dict[str, Any] = {}


def load_tokenizer(
    model_name: str | None = None,
    config: dict[str, Any] | None = None,
) -> Any:
    """Load and cache a HuggingFace tokenizer for the given model."""
    from transformers import AutoTokenizer

    name = model_name or get_model_name(config)
    if name in _tokenizer_cache:
        return _tokenizer_cache[name]

    local_path = get_model_cache_dir(name)
    if not is_model_cached(local_path):
        ensure_model_cached(name)
    load_kwargs = {"local_files_only": True} if is_model_cached(local_path) else {}
    tokenizer = AutoTokenizer.from_pretrained(local_path, **load_kwargs)
    _tokenizer_cache[name] = tokenizer
    return tokenizer


def count_input_tokens(
    text: str,
    model_name: str | None = None,
    config: dict[str, Any] | None = None,
) -> int:
    """Return input token count for text without truncation."""
    if not text:
        return 0
    tokenizer = load_tokenizer(model_name, config)
    return len(tokenizer.encode(text, add_special_tokens=True))


class CodeGenModel:
    """Wrapper for HuggingFace CodeGen models with configurable generation."""

    def __init__(
        self,
        model_name: str,
        device: str = "auto",
        max_length: int = 2048,
        model_path: str | Path | None = None,
        config: dict[str, Any] | None = None,
    ):
        self.model_name = model_name
        self.max_length = max_length
        self.device = resolve_device(device)
        self.config = config
        self.model_path = Path(model_path) if model_path else None
        self.tokenizer = None
        self.model = None
        self._loaded = False
        self._seq2seq = is_seq2seq_model(model_name)

    @staticmethod
    def _build_stop_string_criteria(
        tokenizer: Any,
        stop_strings: list[str],
        prompt_length: int,
    ) -> Any:
        from transformers import StoppingCriteria, StoppingCriteriaList

        class _StopOnSubstring(StoppingCriteria):
            def __init__(self, tok: Any, stops: list[str], start: int) -> None:
                self.tokenizer = tok
                self.stops = stops
                self.start = start

            def __call__(self, input_ids: Any, scores: Any, **kwargs: Any) -> bool:
                text = self.tokenizer.decode(
                    input_ids[0][self.start :],
                    skip_special_tokens=True,
                )
                return any(stop in text for stop in self.stops)

        return StoppingCriteriaList(
            [_StopOnSubstring(tokenizer, stop_strings, prompt_length)]
        )

    def _resolve_local_path(self) -> Path:
        if self.model_path is not None:
            return self.model_path
        return resolve_model_path(self.config)

    def load(self) -> None:
        """Load model and tokenizer from local cache (download first if needed)."""
        if self._loaded:
            return

        from transformers import AutoModelForCausalLM, AutoModelForSeq2SeqLM, AutoTokenizer
        from transformers.utils import logging as transformers_logging

        transformers_logging.set_verbosity_error()

        local_path = self._resolve_local_path()
        load_kwargs = {"local_files_only": True} if is_model_cached(local_path) else {}
        logger.info("Loading model %s from %s on %s", self.model_name, local_path, self.device)
        self.tokenizer = AutoTokenizer.from_pretrained(local_path, **load_kwargs)
        model_cls = AutoModelForSeq2SeqLM if self._seq2seq else AutoModelForCausalLM
        self.model = model_cls.from_pretrained(local_path, **load_kwargs)
        if self.tokenizer.pad_token_id is None:
            self.tokenizer.pad_token = self.tokenizer.eos_token
        self.model.to(self.device)
        self.model.eval()
        self._loaded = True

    def generate(
        self,
        prompt: str,
        max_new_tokens: int = 256,
        temperature: float = 0.2,
        top_p: float = 0.95,
        num_beams: int = 1,
        do_sample: bool = False,
        decoding_strategy: str = "greedy",
        stop_strings: list[str] | None = None,
    ) -> str:
        """Generate text from prompt using greedy or beam search decoding."""
        if not self._loaded:
            self.load()

        import torch

        # Keep the tail of long prompts (question / SQL trigger) when truncating.
        inputs = self.tokenizer(
            prompt,
            return_tensors="pt",
            truncation=True,
            truncation_side="left",
            max_length=self.max_length,
        ).to(self.device)

        input_length = inputs["input_ids"].shape[1]

        gen_kwargs: dict[str, Any] = {
            "max_new_tokens": max_new_tokens,
            "pad_token_id": self.tokenizer.eos_token_id,
        }

        if stop_strings and not self._seq2seq:
            gen_kwargs["stopping_criteria"] = self._build_stop_string_criteria(
                self.tokenizer,
                stop_strings,
                input_length,
            )

        if decoding_strategy == "beam":
            gen_kwargs.update(
                num_beams=max(num_beams, 2),
                do_sample=False,
                early_stopping=True,
            )
        else:
            gen_kwargs.update(
                do_sample=do_sample,
                temperature=temperature if do_sample else 1.0,
                top_p=top_p if do_sample else 1.0,
            )

        with torch.no_grad():
            outputs = self.model.generate(**inputs, **gen_kwargs)

        if self._seq2seq:
            return self.tokenizer.decode(outputs[0], skip_special_tokens=True).strip()

        new_tokens = outputs[0][input_length:]
        return self.tokenizer.decode(new_tokens, skip_special_tokens=True).strip()


def load_model(
    config: dict[str, Any] | None = None,
    device: str | None = None,
    max_length: int | None = None,
    eager: bool = False,
) -> CodeGenModel:
    """Factory function to create and optionally load a CodeGen model."""
    config = config or load_config()
    model_cfg = config.get("model", {})
    model_name = get_model_name(config)

    model = CodeGenModel(
        model_name=model_name,
        device=device or model_cfg.get("device", "auto"),
        max_length=max_length or model_cfg.get("max_length", 2048),
        config=config,
    )
    if eager:
        model.load()
    return model
