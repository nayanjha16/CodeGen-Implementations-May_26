"""
Pre-flight check: verify LoRA target_modules on the configured base model.

Prints attention-related module names and confirms get_peft_model reports
trainable parameters > 0.

Usage:
  python scripts/inspect_lora_modules.py
  python scripts/inspect_lora_modules.py --model Salesforce/codegen-350M-multi
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.utils.config import get_lora_config, get_model_name, load_config


def _attention_module_names(model) -> list[str]:
    keywords = ("attn", "attention", "proj", "qkv", "query", "key", "value")
    names: list[str] = []
    for name, _module in model.named_modules():
        if not name:
            continue
        lower = name.lower()
        if any(keyword in lower for keyword in keywords):
            names.append(name)
    return names


def _leaf_suffixes(module_names: list[str]) -> list[str]:
    suffixes = sorted({name.split(".")[-1] for name in module_names})
    return suffixes


def inspect_model(model_name: str, config_path: Path | None = None) -> int:
    from peft import LoraConfig, get_peft_model, TaskType
    from transformers import AutoModelForCausalLM

    from src.models.model_loader import ensure_model_cached, is_seq2seq_model
    from src.utils.device import resolve_device

    if is_seq2seq_model(model_name):
        print(f"ERROR: {model_name} is seq2seq; this project trains causal LMs only.")
        return 1

    config = load_config(config_path)
    lora_cfg = get_lora_config(config)
    target_modules = list(lora_cfg.get("target_modules") or [])
    if not target_modules:
        print("ERROR: lora.target_modules is empty in config.")
        return 1

    local_path = ensure_model_cached(model_name)
    device = resolve_device(config.get("model", {}).get("device", "auto"))
    print(f"Model: {model_name}")
    print(f"Local path: {local_path}")
    print(f"Device: {device}")
    print(f"Configured target_modules: {target_modules}")
    print()

    model = AutoModelForCausalLM.from_pretrained(local_path, local_files_only=True)
    attn_names = _attention_module_names(model)
    suffixes = _leaf_suffixes(attn_names)

    print("Attention-related module suffixes (leaf names):")
    for suffix in suffixes:
        marker = " <-- configured" if suffix in target_modules else ""
        print(f"  {suffix}{marker}")
    print()

    missing = [name for name in target_modules if name not in suffixes]
    if missing:
        print(f"WARNING: configured target_modules not found as leaf suffixes: {missing}")
        print("Sample full module paths containing each suffix:")
        for suffix in missing:
            matches = [name for name in attn_names if name.endswith(suffix)][:3]
            for match in matches:
                print(f"  {match}")
        print()

    lora_config = LoraConfig(
        r=int(lora_cfg.get("r", 16)),
        lora_alpha=int(lora_cfg.get("lora_alpha", 32)),
        lora_dropout=float(lora_cfg.get("lora_dropout", 0.05)),
        bias=str(lora_cfg.get("bias", "none")),
        target_modules=target_modules,
        task_type=TaskType.CAUSAL_LM,
    )
    peft_model = get_peft_model(model, lora_config)
    trainable, total = peft_model.get_nb_trainable_parameters()
    print(f"Trainable parameters: {trainable:,} / {total:,}")
    if trainable == 0:
        print("ERROR: zero trainable parameters — fix lora.target_modules in config.")
        return 1

    pct = 100.0 * trainable / total if total else 0.0
    print(f"Trainable share: {pct:.4f}%")
    print("OK: LoRA target_modules verified.")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Verify LoRA target_modules on base model.")
    parser.add_argument(
        "--model",
        default=None,
        help="HuggingFace model id (default: MODEL_NAME from .env / config).",
    )
    parser.add_argument(
        "--config",
        default=None,
        help="Path to YAML config (default: configs/default.yaml).",
    )
    args = parser.parse_args()

    config_path = Path(args.config) if args.config else None
    config = load_config(config_path)
    model_name = args.model or get_model_name(config)
    return inspect_model(model_name, config_path)


if __name__ == "__main__":
    raise SystemExit(main())
