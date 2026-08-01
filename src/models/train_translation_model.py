"""Stage 2 training pipeline: Java -> C#.

Uses a fresh copy of the same base model with a separate LoRA adapter, so the
Stage 1 adapter is never modified. Run via `python -m models.train_translation_model`
or `main.py train --stage 2`.
"""
from config.config import CFG
from data.dataset import load_java_csharp_dataset
from data.preprocessing import build_stage2_splits, pairs_to_text_dataset
from models.model_loader import configure_lora, load_base_model
from utils.helpers import get_device, log_gpu_info, set_global_seed
from utils.logger import logger


def _pick_optimizer() -> str:
    try:
        import bitsandbytes  # noqa: F401
        return "paged_adamw_8bit"
    except Exception:
        return "adamw_torch"


def _build_sft_config():
    import torch
    from trl import SFTConfig

    return SFTConfig(
        output_dir=CFG.STAGE2_OUTPUT_DIR,
        num_train_epochs=CFG.STAGE2_EPOCHS,
        per_device_train_batch_size=CFG.STAGE2_BATCH_SIZE,
        gradient_accumulation_steps=CFG.STAGE2_GRAD_ACCUM,
        learning_rate=CFG.STAGE2_LEARNING_RATE,
        lr_scheduler_type="cosine",
        warmup_ratio=0.03,
        weight_decay=0.01,
        logging_steps=CFG.LOGGING_STEPS,
        save_strategy="epoch",
        eval_strategy="epoch",
        optim=_pick_optimizer(),
        fp16=torch.cuda.is_available(),
        bf16=False,
        gradient_checkpointing=True,
        max_seq_length=CFG.STAGE2_MAX_SEQ_LEN,
        dataset_text_field="text",
        packing=False,
        report_to="none",
        seed=CFG.SEED,
    )


def _build_trainer(model, tokenizer, sft_config, train_dataset, eval_dataset):
    from trl import SFTTrainer

    common = dict(model=model, args=sft_config,
                  train_dataset=train_dataset, eval_dataset=eval_dataset)
    try:
        return SFTTrainer(tokenizer=tokenizer, **common)
    except TypeError:
        return SFTTrainer(processing_class=tokenizer, **common)


def train_stage2() -> dict:
    """Run the full Stage 2 (Java -> C#) training pipeline and persist the adapter."""
    set_global_seed(CFG.SEED)
    logger.info("Device: %s", get_device())

    dataset_name, raw_pairs = load_java_csharp_dataset()
    train_pairs, val_pairs = build_stage2_splits(raw_pairs)

    model, tokenizer = load_base_model(max_seq_length=CFG.STAGE2_MAX_SEQ_LEN)
    model = configure_lora(
        model,
        lora_alpha=CFG.STAGE2_LORA_ALPHA,
        max_seq_length=CFG.STAGE2_MAX_SEQ_LEN,
    )

    eos_token = tokenizer.eos_token or "<|endoftext|>"
    train_dataset = pairs_to_text_dataset(train_pairs, eos_token)
    eval_dataset = pairs_to_text_dataset(val_pairs, eos_token)
    logger.info("Stage 2 text datasets built: train=%d, val=%d",
                len(train_dataset), len(eval_dataset))

    sft_config = _build_sft_config()
    trainer = _build_trainer(
        model, tokenizer, sft_config, train_dataset, eval_dataset)

    logger.info(
        "Starting Stage 2 training (Java -> C#) on dataset '%s' ...", dataset_name)
    log_gpu_info("before Stage 2 train")
    stats = trainer.train()
    log_gpu_info("after Stage 2 train")

    save_path = f"{CFG.SAVE_DIR}/stage2_java2csharp_adapter"
    model.save_pretrained(save_path)
    tokenizer.save_pretrained(save_path)
    logger.info("Stage 2 adapter saved to %s", save_path)

    return {"metrics": getattr(stats, "metrics", stats), "dataset": dataset_name, "save_path": save_path}


if __name__ == "__main__":
    train_stage2()
