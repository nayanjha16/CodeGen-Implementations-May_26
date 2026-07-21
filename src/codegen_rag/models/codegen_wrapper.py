"""Thin, reusable wrapper around Salesforce/codegen-350M-multi.

This is the single place that loads the base (or fine-tuned / LoRA-adapted)
model. Every task module (program synthesis, doc-gen, commit messages,
translation, and later SQL/RAG) generates through this wrapper so behavior
(device placement, generation defaults, checkpoint loading) stays consistent.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import torch

from codegen_rag.models.generation_config import GenerationConfig
from codegen_rag.utils.logging_config import get_logger

logger = get_logger(__name__)

__all__ = ["CodeGenModel", "GenerationConfig", "load_model_for_task"]


class CodeGenModel:
    """Loads codegen-350M-multi (optionally with a LoRA adapter, or a fully
    fine-tuned checkpoint) and exposes ``generate`` and ``embed`` for
    downstream task modules.
    """

    def __init__(
        self,
        model_name: str = "Salesforce/codegen-350M-multi",
        adapter_path: Path | str | None = None,
        device: str | None = None,
        dtype: torch.dtype | None = None,
    ):
        from transformers import AutoModelForCausalLM

        self.model_name = model_name
        self.device = device or ("cuda" if torch.cuda.is_available() else "cpu")
        self.dtype = dtype or (torch.float16 if self.device == "cuda" else torch.float32)

        checkpoint_dir = Path(adapter_path) if adapter_path is not None else None

        if checkpoint_dir is not None and not (checkpoint_dir / "adapter_config.json").exists():
            # `adapter_path` is the generic "load fine-tuned weights from
            # here" knob, but CheckpointManager.save() is used by both LoRA
            # runs (which write a small `adapter_config.json` + adapter
            # weights) and *full* fine-tune runs (which write a complete
            # model via `model.save_pretrained()`, e.g. Checkpoint 2's
            # `rust_full`). Only the former is a valid PEFT adapter -- trying
            # to PeftModel.from_pretrained() a full checkpoint raises
            # (HFValidationError -> ValueError: Can't find 'adapter_config.json')
            # because PEFT falls back to treating the local path as a HF Hub
            # repo id. Detect which shape this checkpoint is and load
            # accordingly instead of assuming LoRA.
            if not checkpoint_dir.exists():
                raise FileNotFoundError(f"Checkpoint not found at {checkpoint_dir}")
            logger.info(
                "Loading full fine-tuned checkpoint from %s (no adapter_config.json -> "
                "not a LoRA adapter, loading complete weights directly)",
                checkpoint_dir,
            )
            self.model = AutoModelForCausalLM.from_pretrained(str(checkpoint_dir), torch_dtype=self.dtype)
        else:
            logger.info("Loading base model %s on %s (dtype=%s)", model_name, self.device, self.dtype)
            self.model = AutoModelForCausalLM.from_pretrained(model_name, torch_dtype=self.dtype)
            if checkpoint_dir is not None:
                self._load_adapter(checkpoint_dir)

        self.model.to(self.device)
        self.model.eval()

        from codegen_rag.data.tokenizer_utils import load_tokenizer

        self.tokenizer = load_tokenizer(model_name)
        self.model.resize_token_embeddings(len(self.tokenizer))

    def _load_adapter(self, adapter_path: Path | str) -> None:
        from peft import PeftModel

        adapter_path = Path(adapter_path)
        if not adapter_path.exists():
            raise FileNotFoundError(f"LoRA adapter not found at {adapter_path}")
        logger.info("Attaching LoRA adapter from %s", adapter_path)
        self.model = PeftModel.from_pretrained(self.model, str(adapter_path))

    @torch.inference_mode()
    def generate(self, prompt: str, gen_config: GenerationConfig | None = None) -> list[str]:
        """Generate one or more completions for a single prompt."""
        gen_config = gen_config or GenerationConfig()
        inputs = self.tokenizer(prompt, return_tensors="pt", truncation=True, max_length=512).to(
            self.device
        )
        generate_kwargs: dict[str, Any] = dict(
            max_new_tokens=gen_config.max_new_tokens,
            temperature=gen_config.temperature,
            top_p=gen_config.top_p,
            do_sample=gen_config.do_sample,
            num_return_sequences=gen_config.num_return_sequences,
            pad_token_id=self.tokenizer.pad_token_id,
        )
        if gen_config.stop_sequences:
            # HF `generate()` supports early stopping on literal strings since
            # transformers>=4.34 via `stop_strings` (requires `tokenizer=`).
            generate_kwargs["stop_strings"] = gen_config.stop_sequences
            generate_kwargs["tokenizer"] = self.tokenizer

        outputs = self.model.generate(**inputs, **generate_kwargs)
        input_len = inputs["input_ids"].shape[1]
        completions = [
            self.tokenizer.decode(seq[input_len:], skip_special_tokens=True) for seq in outputs
        ]
        return completions

    def batch_generate(
        self, prompts: list[str], gen_config: GenerationConfig | None = None
    ) -> list[list[str]]:
        """Sequentially generate for a list of prompts (simple, memory-safe default).

        For large-scale evaluation, callers can parallelize by sharding prompts
        across multiple `CodeGenModel` instances / processes.
        """
        return [self.generate(prompt, gen_config) for prompt in prompts]

    @torch.inference_mode()
    def embed(self, texts: list[str], normalize: bool = True) -> torch.Tensor:
        """Mean-pool the final hidden states to get a fixed-size embedding per text.

        Used by the RAG pipeline (Checkpoint 3) for semantic search over the
        FAISS index, and reused here so embedding logic is defined exactly once.
        """
        inputs = self.tokenizer(
            texts, return_tensors="pt", truncation=True, max_length=512, padding=True
        ).to(self.device)
        outputs = self.model(**inputs, output_hidden_states=True)
        hidden = outputs.hidden_states[-1]  # (batch, seq_len, hidden_dim)
        mask = inputs["attention_mask"].unsqueeze(-1).float()
        summed = (hidden * mask).sum(dim=1)
        counts = mask.sum(dim=1).clamp(min=1e-9)
        embeddings = summed / counts
        if normalize:
            embeddings = torch.nn.functional.normalize(embeddings, p=2, dim=1)
        return embeddings.cpu()

    def save_pretrained(self, path: Path) -> None:
        path.mkdir(parents=True, exist_ok=True)
        self.model.save_pretrained(path)
        self.tokenizer.save_pretrained(path)
        logger.info("Saved model + tokenizer to %s", path)


def load_model_for_task(
    settings: Any,
    adapter_path: Path | None = None,
) -> CodeGenModel:
    """Convenience factory reading defaults from Settings."""
    return CodeGenModel(
        model_name=settings.base_model.name,
        adapter_path=adapter_path,
        device=None,
    )
