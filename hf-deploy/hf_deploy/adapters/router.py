"""Multi-adapter PEFT router: one base model, hot-swap via set_adapter."""

from __future__ import annotations

import logging
import threading
from pathlib import Path
from typing import Any

from hf_deploy import INTENTS
from hf_deploy.adapters.resolve import resolve_version_adapters

logger = logging.getLogger("hf_deploy.router")


def _resolve_device(device: str) -> str:
    if device != "auto":
        return device
    try:
        import torch

        if torch.cuda.is_available():
            return "cuda"
        if getattr(torch.backends, "mps", None) and torch.backends.mps.is_available():
            return "mps"
    except Exception:
        pass
    return "cpu"


class MultiAdapterRouter:
    """Load CodeGen once and switch LoRA adapters per request."""

    def __init__(
        self,
        *,
        base_model: str,
        adapter_locations: dict[str, str | Path],
        adapter_source: str = "local",
        checkpoint_version: str | None = None,
        device: str = "auto",
        max_length: int = 2048,
        generation: dict[str, Any] | None = None,
    ) -> None:
        self.base_model = base_model
        self.adapter_source = adapter_source
        self.checkpoint_version = checkpoint_version
        self.adapter_paths = {k: str(v) for k, v in adapter_locations.items()}
        missing = [intent for intent in INTENTS if intent not in self.adapter_paths]
        if missing:
            raise ValueError(f"Missing adapter locations for: {missing}")
        self.device = _resolve_device(device)
        self.max_length = max_length
        self.generation = generation or {}

        self.model: Any = None
        self.tokenizer: Any = None
        self._loaded = False
        self._lock = threading.Lock()

    @classmethod
    def from_manifest(cls, manifest: dict[str, Any]) -> "MultiAdapterRouter":
        """Build a router from a loaded deployment manifest."""
        source = str(manifest.get("adapter_source", "local")).lower()
        if source == "hub":
            locations: dict[str, str | Path] = dict(manifest["hub_adapter_ids"])
        elif source == "local":
            locations = resolve_version_adapters(
                manifest["checkpoints_root"],
                manifest["checkpoint_version"],
                manifest.get("adapters"),
            )
        else:
            raise ValueError(
                f"Unknown adapter_source '{source}'. Use 'local' or 'hub'."
            )
        return cls(
            base_model=manifest["base_model"],
            adapter_locations=locations,
            adapter_source=source,
            checkpoint_version=manifest.get("checkpoint_version"),
            device=manifest.get("device", "auto"),
            generation=manifest.get("generation") or {},
        )

    @property
    def loaded(self) -> bool:
        return self._loaded

    def load(self) -> None:
        """Load base model and all LoRA adapters into memory."""
        with self._lock:
            if self._loaded:
                return
            self._load_unlocked()

    def _load_unlocked(self) -> None:
        from peft import PeftModel
        from transformers import AutoModelForCausalLM, AutoTokenizer

        logger.info(
            "Loading base model %s on %s (source=%s version=%s)",
            self.base_model,
            self.device,
            self.adapter_source,
            self.checkpoint_version,
        )
        self.tokenizer = AutoTokenizer.from_pretrained(self.base_model)
        if self.tokenizer.pad_token_id is None:
            self.tokenizer.pad_token = self.tokenizer.eos_token

        base = AutoModelForCausalLM.from_pretrained(self.base_model)
        primary = INTENTS[0]
        primary_path = self.adapter_paths[primary]
        logger.info("Attaching primary adapter %s from %s", primary, primary_path)
        self.model = PeftModel.from_pretrained(
            base,
            str(primary_path),
            adapter_name=primary,
            is_trainable=False,
        )
        for intent in INTENTS[1:]:
            path = self.adapter_paths[intent]
            logger.info("Loading adapter %s from %s", intent, path)
            self.model.load_adapter(str(path), adapter_name=intent)

        self.model.to(self.device)
        self.model.eval()
        self._loaded = True

    def ensure_loaded(self) -> None:
        if not self._loaded:
            self.load()

    def set_adapter(self, intent: str) -> None:
        """Activate the LoRA adapter for ``intent``."""
        if intent not in INTENTS:
            raise ValueError(f"Unknown adapter intent '{intent}'")
        self.ensure_loaded()
        self.model.set_adapter(intent)

    def generate(
        self,
        prompt: str,
        *,
        intent: str,
        max_new_tokens: int | None = None,
        temperature: float | None = None,
        top_p: float | None = None,
        do_sample: bool | None = None,
    ) -> str:
        """Generate with the adapter selected for ``intent``."""
        import torch

        self.ensure_loaded()
        with self._lock:
            self.model.set_adapter(intent)

            gen_cfg = self.generation
            resolved_max = max_new_tokens
            if resolved_max is None:
                if intent == "nosql2doc":
                    resolved_max = int(
                        gen_cfg.get("documentation_max_new_tokens", 96)
                    )
                else:
                    resolved_max = int(gen_cfg.get("max_new_tokens", 256))

            temperature = (
                float(gen_cfg.get("temperature", 0.2))
                if temperature is None
                else temperature
            )
            top_p = float(gen_cfg.get("top_p", 0.95)) if top_p is None else top_p
            do_sample = (
                bool(gen_cfg.get("do_sample", False))
                if do_sample is None
                else do_sample
            )

            inputs = self.tokenizer(
                prompt,
                return_tensors="pt",
                truncation=True,
                truncation_side="left",
                max_length=self.max_length,
            ).to(self.device)
            input_length = inputs["input_ids"].shape[1]

            gen_kwargs: dict[str, Any] = {
                "max_new_tokens": resolved_max,
                "pad_token_id": self.tokenizer.eos_token_id,
                "do_sample": do_sample,
                "temperature": temperature if do_sample else 1.0,
                "top_p": top_p if do_sample else 1.0,
            }

            with torch.no_grad():
                outputs = self.model.generate(**inputs, **gen_kwargs)

            new_tokens = outputs[0][input_length:]
            return self.tokenizer.decode(new_tokens, skip_special_tokens=True).strip()

    def status(self) -> dict[str, Any]:
        """Return load status and resolved adapter paths."""
        return {
            "loaded": self._loaded,
            "base_model": self.base_model,
            "adapter_source": self.adapter_source,
            "checkpoint_version": self.checkpoint_version,
            "device": self.device,
            "adapters": dict(self.adapter_paths),
        }
