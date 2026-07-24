"""Modular CodeGen model loading with local caching and GPU/CPU support."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

from src.utils.config import get_adapter_name, get_adapter_path, get_adapter_run, get_model_name, load_config
from src.utils.device import resolve_device
from src.utils.paths import (
    ensure_storage_dirs,
    get_checkpoint_path,
    get_model_cache_dir,
    resolve_project_path,
)

logger = logging.getLogger("codegen")


def is_seq2seq_model(model_name: str) -> bool:
    """Return True for encoder-decoder models such as T5."""
    lowered = model_name.lower()
    return any(tag in lowered for tag in ("t5", "bart", "pegasus", "mbart"))


def is_codegen2_model(model_name: str | None) -> bool:
    """Return True for Salesforce CodeGen2 checkpoints (native CodeGen arch)."""
    return "codegen2" in (model_name or "").lower()


_CODEGEN2_MP_NUM = 8  # Hub CodeGen2 remote modeling; native transformers defaults to 4
_codegen_attn_forward_patched = False


def _ensure_codegen_attention_mp_num_hook() -> None:
    """Make native CodeGenAttention honor ``attn._mp_num`` (CodeGen2 needs 8)."""
    global _codegen_attn_forward_patched
    if _codegen_attn_forward_patched:
        return

    import inspect
    import textwrap

    from transformers.models.codegen.modeling_codegen import CodeGenAttention
    import transformers.models.codegen.modeling_codegen as codegen_modeling

    src = inspect.getsource(CodeGenAttention.forward)
    if "mp_num = 4" not in src:
        raise RuntimeError(
            "CodeGenAttention.forward no longer contains 'mp_num = 4'; "
            "update the CodeGen2 compatibility hook."
        )
    src = src.replace(
        "mp_num = 4",
        "mp_num = getattr(self, '_mp_num', 4)",
        1,
    )
    src = textwrap.dedent(src)
    namespace = dict(vars(codegen_modeling))
    exec(src, namespace)
    CodeGenAttention.forward = namespace["forward"]
    _codegen_attn_forward_patched = True
    logger.info("Patched CodeGenAttention.forward to honor attn._mp_num")


def _apply_codegen2_mp_num(model: Any) -> Any:
    """Set CodeGen2 TPU shard factor (mp_num=8) on every attention block."""
    _ensure_codegen_attention_mp_num_hook()
    transformer = getattr(model, "transformer", None)
    layers = getattr(transformer, "h", None) if transformer is not None else None
    if layers is None:
        raise RuntimeError("CodeGen2 model missing transformer.h layers")
    for block in layers:
        block.attn._mp_num = _CODEGEN2_MP_NUM
    return model


def requires_trust_remote_code(
    model_name: str | None = None,
    config: dict[str, Any] | None = None,
) -> bool:
    """Return True when HuggingFace custom model code must be trusted.

    CodeGen2 Hub ``auto_map`` code is incompatible with modern transformers
    (removed ``transformers.onnx``, removed ``get_head_mask``). We load via
    native ``CodeGenForCausalLM`` and set attention ``_mp_num=8`` instead.
    """
    if is_codegen2_model(model_name):
        return False
    if config is not None:
        model_cfg = config.get("model") or {}
        if isinstance(model_cfg, dict) and model_cfg.get("trust_remote_code") is not None:
            return bool(model_cfg.get("trust_remote_code"))
    return False


def hf_load_kwargs(
    model_name: str | None = None,
    config: dict[str, Any] | None = None,
    *,
    local_files_only: bool = False,
) -> dict[str, Any]:
    """Build common ``from_pretrained`` kwargs for this project's models."""
    kwargs: dict[str, Any] = {}
    if local_files_only:
        kwargs["local_files_only"] = True
    if requires_trust_remote_code(model_name, config):
        kwargs["trust_remote_code"] = True
    return kwargs


def _strip_remote_code_from_config(cache_dir: Path) -> None:
    """Remove auto_map / trust_remote_code so local Auto* loads use native CodeGen."""
    import json

    config_path = cache_dir / "config.json"
    if not config_path.exists():
        return
    data = json.loads(config_path.read_text(encoding="utf-8"))
    data.pop("auto_map", None)
    data.pop("trust_remote_code", None)
    config_path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


def _load_codegen2_tokenizer(source: str | Path, **load_kwargs: Any) -> Any:
    """Load CodeGen2 tokenizer (GPT2 + added whitespace/infill tokens)."""
    from transformers import GPT2Tokenizer

    tokenizer = GPT2Tokenizer.from_pretrained(source, **load_kwargs)
    # Hub tokenizer_config caps at 1024; model context is 2048.
    if getattr(tokenizer, "model_max_length", 0) < 2048:
        tokenizer.model_max_length = 2048
    return tokenizer


def _load_codegen2_model(source: str | Path, **load_kwargs: Any) -> Any:
    """Load CodeGen2 with native CodeGen + mp_num=8 attention layout."""
    from transformers import CodeGenForCausalLM

    model = CodeGenForCausalLM.from_pretrained(source, **load_kwargs)
    return _apply_codegen2_mp_num(model)


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

    cache_dir.mkdir(parents=True, exist_ok=True)
    print(f"Downloading model {model_name} to {cache_dir} ...")
    logger.info("Downloading model %s to %s", model_name, cache_dir)

    load_kwargs = hf_load_kwargs(model_name)
    if is_codegen2_model(model_name):
        # Remote CodeGen2 config imports removed transformers.onnx; use native CodeGen.
        tokenizer = _load_codegen2_tokenizer(model_name, **load_kwargs)
        model = _load_codegen2_model(model_name, **load_kwargs)
        tokenizer.save_pretrained(cache_dir)
        model.save_pretrained(cache_dir)
        _strip_remote_code_from_config(cache_dir)
        (cache_dir / ".downloaded").touch()
        return cache_dir

    if causal:
        if is_seq2seq_model(model_name):
            model_cls = AutoModelForSeq2SeqLM
        else:
            model_cls = AutoModelForCausalLM
    else:
        model_cls = AutoModel

    tokenizer = AutoTokenizer.from_pretrained(model_name, **load_kwargs)
    model = model_cls.from_pretrained(model_name, **load_kwargs)
    tokenizer.save_pretrained(cache_dir)
    model.save_pretrained(cache_dir)
    (cache_dir / ".downloaded").touch()
    return cache_dir


def is_adapter_dir(path: str | Path) -> bool:
    """Return True when ``path`` contains a PEFT LoRA adapter."""
    return (Path(path) / "adapter_config.json").is_file()


def resolve_adapter_path(
    adapter: str | None = None,
    adapter_path: str | Path | None = None,
    task: str | None = None,
    config: dict[str, Any] | None = None,
) -> Path | None:
    """Resolve a LoRA adapter under ``models/checkpoints/<model>/<run>/<task>/``.

    Resolution order:
    1. Explicit ``adapter_path`` (absolute, project-relative, or checkpoint name)
    2. ``adapter`` or ``task`` argument
    3. ``MODEL_ADAPTER`` env / ``model.adapter`` config key
    """
    if adapter_path is not None:
        path = Path(adapter_path)
        if not path.is_absolute():
            checkpoint_candidate = get_checkpoint_path(path.name)
            if is_adapter_dir(checkpoint_candidate):
                path = checkpoint_candidate
            else:
                path = resolve_project_path(adapter_path)
    else:
        adapter_name = adapter or task or get_adapter_name(config)
        if not adapter_name:
            return None
        path = get_adapter_path(adapter_name, config, run=get_adapter_run(config))

    if not path.exists():
        raise FileNotFoundError(f"Adapter directory not found: {path}")
    if not is_adapter_dir(path):
        raise FileNotFoundError(
            f"Adapter directory '{path}' is missing adapter_config.json."
        )
    logger.info("Using LoRA adapter at %s", path)
    return path


def resolve_model_path(config: dict[str, Any] | None = None) -> Path:
    """Resolve local full-model path: checkpoint if configured, otherwise cached base model.

    LoRA adapter directories are resolved separately via ``resolve_adapter_path()``.
    """
    config = config or load_config()
    model_cfg = config.get("model", {})

    checkpoint = model_cfg.get("checkpoint") or None
    if checkpoint:
        checkpoint_path = get_checkpoint_path(checkpoint)
        if is_adapter_dir(checkpoint_path):
            raise ValueError(
                f"Checkpoint '{checkpoint}' is a LoRA adapter directory. "
                "Use load_model(adapter=...) or MODEL_ADAPTER instead of MODEL_CHECKPOINT."
            )
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
    load_kwargs = hf_load_kwargs(
        name,
        config,
        local_files_only=is_model_cached(local_path),
    )
    if is_codegen2_model(name):
        tokenizer = _load_codegen2_tokenizer(local_path, **load_kwargs)
    else:
        from transformers import AutoTokenizer

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
    """Wrapper for HuggingFace CodeGen models with configurable generation.

    When ``adapter_path`` is set, the base weights are loaded from ``models/base/``
    and a PEFT LoRA adapter is applied on top for inference.
    """

    def __init__(
        self,
        model_name: str,
        device: str = "auto",
        max_length: int = 2048,
        model_path: str | Path | None = None,
        adapter_path: str | Path | None = None,
        config: dict[str, Any] | None = None,
    ):
        self.model_name = model_name
        self.max_length = max_length
        self.device = resolve_device(device)
        self.config = config
        self.model_path = Path(model_path) if model_path else None
        self.adapter_path = Path(adapter_path) if adapter_path else None
        self.tokenizer = None
        self.model = None
        self._loaded = False
        self._seq2seq = is_seq2seq_model(model_name)
        if self.adapter_path is not None and self._seq2seq:
            raise ValueError("LoRA adapters are supported for causal LM models only.")

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

    def _resolve_tokenizer_path(self) -> Path:
        if self.adapter_path is not None:
            return ensure_model_cached(self.model_name)
        return self._resolve_local_path()

    def load(self) -> None:
        """Load model and tokenizer from local cache (download first if needed)."""
        if self._loaded:
            return

        from transformers import AutoModelForCausalLM, AutoModelForSeq2SeqLM, AutoTokenizer
        from transformers.utils import logging as transformers_logging

        transformers_logging.set_verbosity_error()

        tokenizer_path = self._resolve_tokenizer_path()
        load_kwargs = hf_load_kwargs(
            self.model_name,
            self.config,
            local_files_only=is_model_cached(tokenizer_path),
        )
        logger.info(
            "Loading model %s from %s on %s%s",
            self.model_name,
            tokenizer_path,
            self.device,
            f" with adapter {self.adapter_path}" if self.adapter_path else "",
        )
        if is_codegen2_model(self.model_name):
            self.tokenizer = _load_codegen2_tokenizer(tokenizer_path, **load_kwargs)
        else:
            self.tokenizer = AutoTokenizer.from_pretrained(tokenizer_path, **load_kwargs)
        if self.tokenizer.pad_token_id is None:
            self.tokenizer.pad_token = self.tokenizer.eos_token

        if self.adapter_path is not None:
            if not is_adapter_dir(self.adapter_path):
                raise FileNotFoundError(
                    f"LoRA adapter not found at {self.adapter_path} "
                    "(expected adapter_config.json)."
                )
            from peft import PeftModel

            if is_codegen2_model(self.model_name):
                base_model = _load_codegen2_model(tokenizer_path, **load_kwargs)
            else:
                base_model = AutoModelForCausalLM.from_pretrained(
                    tokenizer_path,
                    **load_kwargs,
                )
            self.model = PeftModel.from_pretrained(
                base_model,
                str(self.adapter_path),
                is_trainable=False,
            )
        else:
            local_path = self._resolve_local_path()
            load_kwargs = hf_load_kwargs(
                self.model_name,
                self.config,
                local_files_only=is_model_cached(local_path),
            )
            if is_codegen2_model(self.model_name):
                self.model = _load_codegen2_model(local_path, **load_kwargs)
            else:
                model_cls = (
                    AutoModelForSeq2SeqLM if self._seq2seq else AutoModelForCausalLM
                )
                self.model = model_cls.from_pretrained(local_path, **load_kwargs)

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
    adapter: str | None = None,
    adapter_path: str | Path | None = None,
    task: str | None = None,
) -> CodeGenModel:
    """Create and optionally load a CodeGen model, with optional LoRA adapter.

    Args:
        adapter: Task name whose adapter lives under ``models/checkpoints/<model>/<run>/<task>/``.
        adapter_path: Explicit adapter directory (overrides ``adapter`` / env).
        task: Alias for ``adapter``.
    """
    config = config or load_config()
    model_cfg = config.get("model", {})
    model_name = get_model_name(config)
    resolved_adapter = resolve_adapter_path(
        adapter=adapter,
        adapter_path=adapter_path,
        task=task,
        config=config,
    )

    model = CodeGenModel(
        model_name=model_name,
        device=device or model_cfg.get("device", "auto"),
        max_length=max_length or model_cfg.get("max_length", 2048),
        adapter_path=resolved_adapter,
        config=config,
    )
    if eager:
        model.load()
    return model
