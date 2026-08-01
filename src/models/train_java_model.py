"""Stage 1 training pipeline: Natural Language -> Java.

Run directly with `python -m models.train_java_model` or via `main.py train --stage 1`.
"""
from config.config import CFG
from data.dataset import STAGE1_CODE_COL, STAGE1_DOC_COL, load_code_dataset, validate_dataset
from data.preprocessing import build_stage1_prompt_dataset
from models.model_loader import configure_lora, load_base_model
from utils.helpers import get_device, log_gpu_info, set_global_seed
from utils.logger import logger


def _build_sft_config():
    import torch
    from trl import SFTConfig

    return SFTConfig(
        output_dir=CFG.STAGE1_OUTPUT_DIR,
        num_train_epochs=CFG.EPOCHS,
        per_device_train_batch_size=CFG.BATCH_SIZE,
        gradient_accumulation_steps=CFG.GRAD_ACCUM,
        learning_rate=CFG.LEARNING_RATE,
        save_strategy=CFG.SAVE_STRATEGY,
        logging_steps=CFG.LOGGING_STEPS,
        dataset_text_field="prompt",
        max_seq_length=CFG.MAX_LENGTH,
        fp16=torch.cuda.is_available(),
        seed=CFG.SEED,
        report_to="none",
    )


def _build_trainer(model, tokenizer, sft_config, train_dataset, n_samples: int = CFG.STAGE1_TRAIN_SAMPLES):
    from trl import SFTTrainer

    n = min(n_samples, len(train_dataset))
    if n <= 0:
        raise ValueError("No training samples available for Stage 1.")

    subset = train_dataset.select(range(n))
    common = dict(model=model, args=sft_config, train_dataset=subset)
    try:
        return SFTTrainer(tokenizer=tokenizer, **common)
    except TypeError:
        # Newer TRL replaced `tokenizer` with `processing_class`.
        return SFTTrainer(processing_class=tokenizer, **common)


def train_stage1() -> dict:
    """Run the full Stage 1 (NL -> Java) training pipeline and persist the adapter."""
    set_global_seed(CFG.SEED)
    logger.info("Device: %s", get_device())

    dataset = load_code_dataset("train")
    validate_dataset(dataset, [STAGE1_DOC_COL, STAGE1_CODE_COL])

    model, tokenizer = load_base_model()
    model = configure_lora(model)

    prompt_dataset = build_stage1_prompt_dataset(dataset, tokenizer)

    sft_config = _build_sft_config()
    trainer = _build_trainer(model, tokenizer, sft_config, prompt_dataset)

    logger.info("Starting Stage 1 training (NL -> Java) ...")
    log_gpu_info("before Stage 1 train")
    stats = trainer.train()
    log_gpu_info("after Stage 1 train")

    save_path = f"{CFG.SAVE_DIR}/stage1_nl2java_adapter"
    model.save_pretrained(save_path)
    tokenizer.save_pretrained(save_path)
    logger.info("Stage 1 adapter saved to %s", save_path)

    return {"metrics": getattr(stats, "metrics", stats), "save_path": save_path}


if __name__ == "__main__":
    train_stage1()
