"""
============================================================
RepoCoder Studio
trainer.py  —  v2.4
============================================================

LoRA training module for the Combined Stage student model.
"""

from __future__ import annotations

from src.config import CONFIG, AppConfig
from src.logger import LOG, SectionPrinter, SummaryPrinter
from src.checkpoint_manager import CheckpointManager


class RepoCoderTrainer:
    """Fine-tunes the student model using LoRA over task-contract prompts."""

    def __init__(self, config: AppConfig = CONFIG):
        self.config = config
        self.checkpoints = CheckpointManager(config)
        self.model = None
        self.tokenizer = None
        self.trainer = None

    def load_model_and_tokenizer(self):
        SectionPrinter.header("Loading Student Model")
        import torch
        from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig

        model_name = self.config.models.student_model_name
        tokenizer = AutoTokenizer.from_pretrained(model_name, trust_remote_code=True)
        if tokenizer.pad_token is None:
            tokenizer.pad_token = tokenizer.eos_token
        tokenizer.padding_side = "right"

        model_kwargs = {"trust_remote_code": True, "device_map": "auto"}
        if self.config.models.use_4bit and torch.cuda.is_available():
            model_kwargs["quantization_config"] = BitsAndBytesConfig(
                load_in_4bit=True,
                bnb_4bit_quant_type="nf4",
                bnb_4bit_compute_dtype=torch.float16,
                bnb_4bit_use_double_quant=True,
            )
        elif torch.cuda.is_available():
            model_kwargs["torch_dtype"] = torch.float16

        model = AutoModelForCausalLM.from_pretrained(model_name, **model_kwargs)
        model.config.use_cache = False
        self.model = model
        self.tokenizer = tokenizer
        LOG.info(f"Loaded model: {model_name}")
        return model, tokenizer

    def prepare_lora_model(self):
        SectionPrinter.header("Preparing LoRA Model")
        from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training
        assert self.model is not None, "Model must be loaded first."
        if self.config.models.use_4bit:
            self.model = prepare_model_for_kbit_training(self.model)
        lora_config = LoraConfig(
            r=self.config.training.lora_rank,
            lora_alpha=self.config.training.lora_alpha,
            lora_dropout=self.config.training.lora_dropout,
            bias="none",
            task_type="CAUSAL_LM",
            target_modules=["q_proj", "k_proj", "v_proj", "o_proj", "gate_proj", "up_proj", "down_proj"],
        )
        self.model = get_peft_model(self.model, lora_config)
        self.model.print_trainable_parameters()
        return self.model

    def train(self, train_dataset, validation_dataset):
        SectionPrinter.header("LoRA Training  [v2.4]")
        import json
        import torch
        import pandas as pd
        from transformers import TrainingArguments
        from trl import SFTTrainer

        if self.model is None or self.tokenizer is None:
            self.load_model_and_tokenizer()
        self.prepare_lora_model()

        epochs = self.config.training.num_train_epochs_demo if self.config.runtime.run_mode == "demo" else self.config.training.num_train_epochs_full
        save_steps = self.config.training.save_steps_demo if self.config.runtime.run_mode == "demo" else self.config.training.save_steps_full

        training_args = TrainingArguments(
            output_dir=self.checkpoints.training_output_dir(),
            num_train_epochs=epochs,
            per_device_train_batch_size=self.config.training.per_device_train_batch_size,
            gradient_accumulation_steps=self.config.training.gradient_accumulation_steps,
            learning_rate=self.config.training.learning_rate,
            warmup_ratio=self.config.training.warmup_ratio,
            weight_decay=self.config.training.weight_decay,
            logging_steps=self.config.training.logging_steps,
            save_steps=save_steps,
            save_total_limit=self.config.training.save_total_limit,
            fp16=torch.cuda.is_available(),
            report_to="none",
            eval_strategy="steps",
            eval_steps=save_steps,
            gradient_checkpointing=True,
        )

        trainer = SFTTrainer(
            model=self.model,
            tokenizer=self.tokenizer,
            train_dataset=train_dataset,
            eval_dataset=validation_dataset,
            dataset_text_field="text",
            max_seq_length=self.config.models.max_seq_length,
            packing=False,
            args=training_args,
        )

        resume_checkpoint = self.checkpoints.should_resume()
        trainer.train(resume_from_checkpoint=resume_checkpoint)

        final_adapter_dir = self.checkpoints.final_adapter_dir()
        trainer.model.save_pretrained(final_adapter_dir)
        self.tokenizer.save_pretrained(final_adapter_dir)

        reports_dir = self.config.storage.project_root() / self.config.storage.reports_dir
        reports_dir.mkdir(parents=True, exist_ok=True)
        history = trainer.state.log_history or []
        history_path = reports_dir / "training_history.csv"
        pd.DataFrame(history).to_csv(history_path, index=False)
        summary = {
            "train_rows": len(train_dataset),
            "validation_rows": len(validation_dataset),
            "final_adapter": str(final_adapter_dir),
            "epochs": epochs,
            "save_steps": save_steps,
            "global_step": trainer.state.global_step,
            "best_model_checkpoint": trainer.state.best_model_checkpoint,
            "log_history_rows": len(history),
            "prompt_version": "task_contract_v2.4",
            "task_interference_mitigation": "explicit_task_contract_prompt",
        }
        summary_path = reports_dir / "training_summary.json"
        summary_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")

        self.trainer = trainer
        SummaryPrinter.print_summary(
            "Training Summary  [v2.4]",
            {
                "Train Rows": len(train_dataset),
                "Validation Rows": len(validation_dataset),
                "Final Adapter": str(final_adapter_dir),
                "Training History": str(history_path),
                "Training Summary": str(summary_path),
            },
        )
        return trainer
