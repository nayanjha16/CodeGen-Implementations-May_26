"""LoRA continuation trainer that preserves a parent adapter as a separate artifact."""

from __future__ import annotations

from pathlib import Path

from src.trainer import RepoCoderTrainer


class AdapterContinuationTrainer(RepoCoderTrainer):
    """Continue training from an existing LoRA adapter into a new output path."""

    def __init__(self, source_adapter_dir: Path, config):
        super().__init__(config)
        self.source_adapter_dir = Path(source_adapter_dir)

    def prepare_lora_model(self):
        from peft import PeftModel, prepare_model_for_kbit_training

        if self.model is None:
            raise RuntimeError("Load the base model before attaching the parent adapter.")
        if not (self.source_adapter_dir / "adapter_config.json").is_file():
            raise FileNotFoundError(f"Parent adapter is incomplete: {self.source_adapter_dir}")

        if self.config.models.use_4bit:
            self.model = prepare_model_for_kbit_training(self.model)
        self.model = PeftModel.from_pretrained(
            self.model,
            str(self.source_adapter_dir),
            is_trainable=True,
        )
        self.model.print_trainable_parameters()
        return self.model

