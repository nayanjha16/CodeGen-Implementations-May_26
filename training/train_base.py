"""Shared training logic for NL2Py and Java2Py fine-tuning."""

import argparse
import sys
from pathlib import Path
from typing import Any, cast

# Path setup MUST happen before the local (lora_config) and project
# (utils.device) imports below, otherwise they fail when train_base.py is
# imported or run directly rather than via train_java2py.py / train_nl2py.py.
SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent
for _p in (str(SCRIPT_DIR), str(PROJECT_ROOT)):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import yaml
from datasets import load_from_disk
from peft import PeftModel
from transformers import AutoModelForCausalLM, AutoTokenizer
from trl import SFTConfig, SFTTrainer  # pyright: ignore[reportPrivateImportUsage]

from lora_config import apply_lora, get_lora_config
from utils.device import (
    apply_mac_training_overrides,
    describe_device,
    get_best_device,
    get_inference_dtype,
    get_training_precision,
)


def load_config(config_path: str) -> dict:
    with open(config_path) as f:
        return yaml.safe_load(f)


def train(config: dict):
    device = get_best_device(config.get("device", "auto"))
    config = apply_mac_training_overrides(config, device)
    precision = get_training_precision(device)
    dtype = get_inference_dtype(device)

    model_name = config["model_name"]
    local_model = PROJECT_ROOT / model_name
    if local_model.exists():
        model_name = str(local_model)
    dataset_path = PROJECT_ROOT / config["dataset_path"]
    output_dir = PROJECT_ROOT / config["output_dir"]
    output_dir.mkdir(parents=True, exist_ok=True)

    print(f"Training on {describe_device(device)} (dtype={dtype})")
    print(f"Precision: fp16={precision['fp16']}, bf16={precision['bf16']}")

    print(f"Loading tokenizer and model: {model_name}")
    tokenizer = AutoTokenizer.from_pretrained(model_name, trust_remote_code=True)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    # HF from_pretrained returns a dynamic union the type-checker cannot
    # reconcile with nn.Module/PEFT APIs; cast to Any (same pattern as
    # inference/generator.py) to avoid false-positive type errors.
    model: Any = cast(
        Any,
        AutoModelForCausalLM.from_pretrained(
            model_name,
            trust_remote_code=True,
            torch_dtype=dtype,
        ),
    )
    if device != "cpu":
        model = model.to(device)

    lora_config = get_lora_config(
        r=config.get("lora_r", 16),
        lora_alpha=config.get("lora_alpha", 32),
        lora_dropout=config.get("lora_dropout", 0.05),
        target_modules=config.get("lora_target_modules"),
    )
    model = apply_lora(model, lora_config)

    print(f"Loading datasets from {dataset_path}")
    train_ds: Any = load_from_disk(str(dataset_path / "train"))
    val_ds: Any = load_from_disk(str(dataset_path / "val"))

    training_args = SFTConfig(
        output_dir=str(output_dir),
        num_train_epochs=config.get("num_train_epochs", 3),
        per_device_train_batch_size=config.get("per_device_train_batch_size", 8),
        per_device_eval_batch_size=config.get("per_device_eval_batch_size", 8),
        gradient_accumulation_steps=config.get("gradient_accumulation_steps", 4),
        learning_rate=config.get("learning_rate", 2e-4),
        warmup_ratio=config.get("warmup_ratio", 0.03),
        weight_decay=config.get("weight_decay", 0.01),
        fp16=config.get("fp16", precision["fp16"]),
        bf16=config.get("bf16", precision["bf16"]),
        use_cpu=False,
        logging_steps=config.get("logging_steps", 10),
        eval_strategy=config.get("eval_strategy", "epoch"),
        save_strategy=config.get("save_strategy", "epoch"),
        save_total_limit=config.get("save_total_limit", 2),
        load_best_model_at_end=config.get("load_best_model_at_end", True),
        metric_for_best_model=config.get("metric_for_best_model", "eval_loss"),
        greater_is_better=config.get("greater_is_better", False),
        seed=config.get("seed", 42),
        report_to="none",
        max_length=config.get("max_seq_length", 512),
        dataset_text_field="text",
    )

    trainer = SFTTrainer(
        model=model,
        args=training_args,
        train_dataset=train_ds,
        eval_dataset=val_ds,
        processing_class=tokenizer,
    )

    print("Starting training...")
    trainer.train()

    # Save LoRA adapter
    adapter_dir = output_dir / "adapter"
    trained_model: Any = trainer.model
    trained_model.save_pretrained(str(adapter_dir))
    tokenizer.save_pretrained(str(adapter_dir))
    print(f"LoRA adapter saved to {adapter_dir}")

    # Merge and save full model for inference
    print("Merging LoRA weights...")
    merged_dir = output_dir / "merged"
    base_model: Any = cast(
        Any,
        AutoModelForCausalLM.from_pretrained(
            model_name,
            trust_remote_code=True,
            torch_dtype="auto",
        ),
    )
    merged_model: Any = PeftModel.from_pretrained(base_model, str(adapter_dir))
    merged_model = merged_model.merge_and_unload()
    merged_model.save_pretrained(str(merged_dir))
    tokenizer.save_pretrained(str(merged_dir))
    print(f"Merged model saved to {merged_dir}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", required=True, help="Path to YAML config")
    args = parser.parse_args()
    config = load_config(args.config)
    train(config)


if __name__ == "__main__":
    main()
