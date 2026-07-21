"""LoRA (and full) fine-tuning pipeline for extending codegen-350M-multi to
Rust (Task 4 / new-language extension).

Checkpoint 1 uses this module in its "subset" mode (500 samples, LoRA,
r=16/alpha=32/dropout=0.05, ~3 epochs) to establish an initial CodeBLEU
baseline. Checkpoint 2 reuses the exact same trainer in "full" mode (full
corpus, continued pretraining, 5 epochs) — see ``configs/training_config.yaml``.
"""

from __future__ import annotations

import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import torch
from torch.utils.data import DataLoader, Dataset

from codegen_rag.training.checkpoint_manager import CheckpointManager
from codegen_rag.utils.logging_config import get_logger

logger = get_logger(__name__)


@dataclass
class TrainingResult:
    final_loss: float
    steps_completed: int
    epochs_completed: int
    checkpoint_dir: str
    loss_history: list[dict[str, float]]


class LoRAFineTuner:
    """Fine-tunes codegen-350M-multi with a LoRA adapter (fallback / Checkpoint-1
    default) or full-parameter continued pretraining (Checkpoint-2 primary path,
    selected via ``approach="full"``).
    """

    def __init__(
        self,
        model_name: str,
        output_dir: Path,
        approach: str = "lora",
        lora_r: int = 16,
        lora_alpha: int = 32,
        lora_dropout: float = 0.05,
        lora_target_modules: list[str] | None = None,
        learning_rate: float = 2e-4,
        batch_size: int = 8,
        gradient_accumulation_steps: int = 2,
        epochs: int = 3,
        warmup_ratio: float = 0.06,
        weight_decay: float = 0.01,
        max_grad_norm: float = 1.0,
        logging_steps: int = 10,
        save_steps: int = 50,
        eval_steps: int = 25,
        mixed_precision: str = "fp16",
        use_tensorboard: bool = True,
        use_wandb: bool = False,
        wandb_project: str = "codegen-rag-capstone",
        wandb_run_name: str | None = None,
        save_total_limit: int = 2,
    ):
        self.model_name = model_name
        self.output_dir = output_dir
        self.approach = approach
        self.lora_r = lora_r
        self.lora_alpha = lora_alpha
        self.lora_dropout = lora_dropout
        self.lora_target_modules = lora_target_modules or ["qkv_proj", "out_proj", "fc_in", "fc_out"]
        self.learning_rate = learning_rate
        self.batch_size = batch_size
        self.gradient_accumulation_steps = gradient_accumulation_steps
        self.epochs = epochs
        self.warmup_ratio = warmup_ratio
        self.weight_decay = weight_decay
        self.max_grad_norm = max_grad_norm
        self.logging_steps = logging_steps
        self.save_steps = save_steps
        self.eval_steps = eval_steps
        self.mixed_precision = mixed_precision
        self.use_tensorboard = use_tensorboard
        self.use_wandb = use_wandb
        self.wandb_project = wandb_project
        self.wandb_run_name = wandb_run_name or f"{approach}-finetune-{int(time.time())}"

        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.checkpoint_manager = CheckpointManager(output_dir, save_total_limit=save_total_limit)

    def _build_model(self):
        from transformers import AutoModelForCausalLM

        model = AutoModelForCausalLM.from_pretrained(self.model_name, torch_dtype=torch.float32)
        model.config.use_cache = False  # incompatible with gradient checkpointing during training

        if self.approach == "lora":
            from peft import LoraConfig, get_peft_model

            lora_config = LoraConfig(
                r=self.lora_r,
                lora_alpha=self.lora_alpha,
                lora_dropout=self.lora_dropout,
                target_modules=self.lora_target_modules,
                bias="none",
                task_type="CAUSAL_LM",
            )
            model = get_peft_model(model, lora_config)
            trainable, total = model.get_nb_trainable_parameters()
            logger.info(
                "LoRA attached: %d trainable / %d total params (%.2f%%)",
                trainable,
                total,
                100 * trainable / total,
            )
        else:
            logger.info("Full fine-tuning: all %d params trainable", sum(p.numel() for p in model.parameters()))

        model.gradient_checkpointing_enable()
        if self.approach == "lora":
            model.enable_input_require_grads()

        return model.to(self.device)

    def _build_writers(self):
        tb_writer = None
        if self.use_tensorboard:
            from torch.utils.tensorboard import SummaryWriter

            tb_writer = SummaryWriter(log_dir=str(self.output_dir / "tensorboard"))

        wandb_run = None
        if self.use_wandb:
            try:
                import wandb

                wandb_run = wandb.init(
                    project=self.wandb_project,
                    name=self.wandb_run_name,
                    config={
                        "approach": self.approach,
                        "learning_rate": self.learning_rate,
                        "batch_size": self.batch_size,
                        "epochs": self.epochs,
                    },
                )
            except Exception as exc:  # pragma: no cover - optional dependency
                logger.warning("Could not initialize W&B (%s); continuing without it", exc)

        return tb_writer, wandb_run

    def train(
        self,
        train_dataset: Dataset,
        val_dataset: Dataset | None = None,
        resume: bool = True,
    ) -> TrainingResult:
        if self.device == "cuda":
            torch.cuda.empty_cache()

        resume_meta = self.checkpoint_manager.find_resume_point("latest") if resume else None
        start_step = resume_meta.step if resume_meta else 0
        start_epoch = resume_meta.epoch if resume_meta else 0

        if resume_meta and self.approach == "full":
            from transformers import AutoModelForCausalLM

            model = AutoModelForCausalLM.from_pretrained(
                resume_meta.checkpoint_dir, torch_dtype=torch.float32
            )
            model.config.use_cache = False
            model.gradient_checkpointing_enable()
            model = model.to(self.device)
            logger.info(
                "Resumed full fine-tune weights from %s (step %d, epoch %d)",
                resume_meta.checkpoint_dir, start_step, start_epoch,
            )
        else:
            model = self._build_model()
            if resume_meta and self.approach == "lora":
                from peft import PeftModel

                model = PeftModel.from_pretrained(model, resume_meta.checkpoint_dir, is_trainable=True)
                model = model.to(self.device)
                logger.info(
                    "Resumed LoRA adapter from %s (step %d, epoch %d)",
                    resume_meta.checkpoint_dir, start_step, start_epoch,
                )

        train_loader = DataLoader(train_dataset, batch_size=self.batch_size, shuffle=True)
        val_loader = (
            DataLoader(val_dataset, batch_size=self.batch_size, shuffle=False) if val_dataset else None
        )

        optimizer = torch.optim.AdamW(
            model.parameters(), lr=self.learning_rate, weight_decay=self.weight_decay
        )
        total_steps = max(1, (len(train_loader) // self.gradient_accumulation_steps) * self.epochs)
        warmup_steps = int(total_steps * self.warmup_ratio)
        scheduler = torch.optim.lr_scheduler.LambdaLR(
            optimizer, lr_lambda=self._lr_lambda(warmup_steps, total_steps)
        )

        if start_step >= total_steps:
            logger.info(
                "Resumed step %d already reached total_steps=%d; nothing further to train.",
                start_step, total_steps,
            )
            return TrainingResult(
                final_loss=resume_meta.loss if resume_meta else float("nan"),
                steps_completed=start_step,
                epochs_completed=self.epochs,
                checkpoint_dir=resume_meta.checkpoint_dir if resume_meta else "",
                loss_history=[],
            )

        scaler = torch.cuda.amp.GradScaler(enabled=(self.mixed_precision == "fp16" and self.device == "cuda"))
        tb_writer, wandb_run = self._build_writers()

        model.train()
        global_step = start_step
        loss_history: list[dict[str, float]] = []
        best_loss = float("inf")

        for epoch in range(start_epoch, self.epochs):
            if global_step >= total_steps:
                break
            for batch_idx, batch in enumerate(train_loader):
                if global_step >= total_steps:
                    break
                batch = {k: torch.as_tensor(v).to(self.device) for k, v in batch.items()}

                with torch.autocast(
                    device_type=self.device, enabled=(self.mixed_precision == "fp16")
                ):
                    outputs = model(**batch)
                    loss = outputs.loss / self.gradient_accumulation_steps

                scaler.scale(loss).backward()

                if (batch_idx + 1) % self.gradient_accumulation_steps == 0:
                    scaler.unscale_(optimizer)
                    torch.nn.utils.clip_grad_norm_(model.parameters(), self.max_grad_norm)
                    scaler.step(optimizer)
                    scaler.update()
                    scheduler.step()
                    optimizer.zero_grad()
                    global_step += 1

                    step_loss = loss.item() * self.gradient_accumulation_steps
                    best_loss = min(best_loss, step_loss)

                    if global_step % self.logging_steps == 0:
                        lr = scheduler.get_last_lr()[0]
                        logger.info(
                            "epoch=%d step=%d loss=%.4f lr=%.2e", epoch, global_step, step_loss, lr
                        )
                        loss_history.append({"step": global_step, "epoch": epoch, "loss": step_loss})
                        if tb_writer:
                            tb_writer.add_scalar("train/loss", step_loss, global_step)
                            tb_writer.add_scalar("train/lr", lr, global_step)
                        if wandb_run:
                            wandb_run.log({"train/loss": step_loss, "train/lr": lr, "step": global_step})

                    if val_loader and global_step % self.eval_steps == 0:
                        val_loss = self._evaluate(model, val_loader)
                        logger.info("epoch=%d step=%d val_loss=%.4f", epoch, global_step, val_loss)
                        if tb_writer:
                            tb_writer.add_scalar("val/loss", val_loss, global_step)
                        if wandb_run:
                            wandb_run.log({"val/loss": val_loss, "step": global_step})
                        model.train()

                    if global_step % self.save_steps == 0:
                        self.checkpoint_manager.save(model, global_step, epoch, step_loss)

                    if global_step >= total_steps:
                        break

        final_loss = loss_history[-1]["loss"] if loss_history else float("nan")
        final_meta = self.checkpoint_manager.save(model, global_step, self.epochs - 1, final_loss)
    @torch.inference_mode()
    def _evaluate(self, model: Any, val_loader: DataLoader) -> float:
        model.eval()
        total_loss, n_batches = 0.0, 0
        for batch in val_loader:
            batch = {k: torch.as_tensor(v).to(self.device) for k, v in batch.items()}
            outputs = model(**batch)
            total_loss += outputs.loss.item()
            n_batches += 1
        return total_loss / max(1, n_batches)

    @staticmethod
    def _lr_lambda(warmup_steps: int, total_steps: int):
        def _fn(step: int) -> float:
            if step < warmup_steps:
                return step / max(1, warmup_steps)
            progress = (step - warmup_steps) / max(1, total_steps - warmup_steps)
            return max(0.0, 1.0 - progress)

        return _fn
