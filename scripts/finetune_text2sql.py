"""
Fine-tune a text-to-SQL model on Spider.

Raw encoder-decoder models such as google-t5/t5-base do not generate SQL out of
the box. Run this script once, then point MODEL_CHECKPOINT at the saved run.

Usage:
  python scripts/finetune_text2sql.py --epochs 3 --output spider-t5-base
  MODEL_CHECKPOINT=spider-t5-base python scripts/run_baseline_eval.py --dataset spider
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.datasets.spider_loader import SpiderLoader
from src.text2sql.prompt_builder import PromptBuilder
from src.utils.config import get_model_name, load_config
from src.utils.paths import get_checkpoint_path
from src.utils.seeds import set_seeds


def build_dataset(examples: list[dict[str, str]], prompt_builder: PromptBuilder):
    from datasets import Dataset

    rows = []
    for ex in examples:
        if not ex.get("sql"):
            continue
        rows.append(
            {
                "input_text": prompt_builder.build(ex["question"], ex.get("schema", "")),
                "target_text": ex["sql"].strip(),
            }
        )
    return Dataset.from_list(rows)


def main() -> None:
    parser = argparse.ArgumentParser(description="Fine-tune text-to-SQL on Spider")
    parser.add_argument("--epochs", type=int, default=3)
    parser.add_argument("--batch-size", type=int, default=4)
    parser.add_argument("--learning-rate", type=float, default=3e-4)
    parser.add_argument("--max-train-samples", type=int, default=0, help="0 = all")
    parser.add_argument("--max-val-samples", type=int, default=256)
    parser.add_argument("--output", default="spider-t5-base", help="checkpoint folder name")
    parser.add_argument("--split", default="train")
    args = parser.parse_args()

    config = load_config()
    set_seeds(config)
    model_name = get_model_name(config)

    from src.models.model_loader import ensure_model_cached, is_seq2seq_model

    if not is_seq2seq_model(model_name):
        raise ValueError(
            f"{model_name} is not a seq2seq model. "
            "Fine-tuning script currently supports T5/BART-style models."
        )

    ensure_model_cached(model_name)
    prompt_builder = PromptBuilder.for_model(model_name, config)

    loader = SpiderLoader(config=config)
    train_examples = loader.load_split(args.split)
    val_examples = loader.load_split("validation")

    if args.max_train_samples:
        train_examples = train_examples[: args.max_train_samples]
    if args.max_val_samples:
        val_examples = val_examples[: args.max_val_samples]

    train_ds = build_dataset(train_examples, prompt_builder)
    val_ds = build_dataset(val_examples, prompt_builder)

    from transformers import (
        AutoModelForSeq2SeqLM,
        AutoTokenizer,
        DataCollatorForSeq2Seq,
        Seq2SeqTrainer,
        Seq2SeqTrainingArguments,
    )

    from src.models.model_loader import resolve_model_path

    model_path = resolve_model_path(config)
    tokenizer = AutoTokenizer.from_pretrained(model_path, local_files_only=True)
    model = AutoModelForSeq2SeqLM.from_pretrained(model_path, local_files_only=True)
    if tokenizer.pad_token_id is None:
        tokenizer.pad_token = tokenizer.eos_token

    max_input = config.get("model", {}).get("max_length", 512)
    max_target = config.get("generation", {}).get("max_new_tokens", 256)

    def tokenize(batch):
        model_inputs = tokenizer(
            batch["input_text"],
            max_length=max_input,
            truncation=True,
        )
        labels = tokenizer(
            text_target=batch["target_text"],
            max_length=max_target,
            truncation=True,
        )
        model_inputs["labels"] = labels["input_ids"]
        return model_inputs

    train_ds = train_ds.map(tokenize, batched=True, remove_columns=train_ds.column_names)
    val_ds = val_ds.map(tokenize, batched=True, remove_columns=val_ds.column_names)

    output_dir = get_checkpoint_path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)

    training_args = Seq2SeqTrainingArguments(
        output_dir=str(output_dir),
        num_train_epochs=args.epochs,
        per_device_train_batch_size=args.batch_size,
        per_device_eval_batch_size=args.batch_size,
        learning_rate=args.learning_rate,
        predict_with_generate=True,
        eval_strategy="epoch",
        save_strategy="epoch",
        logging_steps=50,
        save_total_limit=2,
        load_best_model_at_end=True,
        metric_for_best_model="eval_loss",
        report_to=[],
    )

    trainer = Seq2SeqTrainer(
        model=model,
        args=training_args,
        train_dataset=train_ds,
        eval_dataset=val_ds,
        processing_class=tokenizer,
        data_collator=DataCollatorForSeq2Seq(tokenizer, model=model),
    )

    print(f"Training {model_name} on {len(train_examples)} Spider examples ...")
    trainer.train()
    trainer.save_model(str(output_dir))
    tokenizer.save_pretrained(str(output_dir))
    print(f"Saved checkpoint to {output_dir}")
    print(f"Set MODEL_CHECKPOINT={args.output} in .env and re-run baseline eval.")


if __name__ == "__main__":
    main()
