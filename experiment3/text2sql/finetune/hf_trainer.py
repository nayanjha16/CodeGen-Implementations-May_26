from pathlib import Path

class HFTrainer:
    """Fallback LoRA fine-tuning via HuggingFace PEFT + Trainer."""

    def __init__(self, repo: str, lora_rank: int = 16, epochs: int = 3,
                 batch_size: int = 4, learning_rate: float = 2e-4):
        self.repo = repo
        self.lora_rank = lora_rank
        self.epochs = epochs
        self.batch_size = batch_size
        self.learning_rate = learning_rate

    def train(self, train_jsonl: Path, valid_jsonl: Path, adapter_out: Path) -> Path:
        import json
        import torch
        from datasets import Dataset
        from transformers import (AutoModelForCausalLM, AutoTokenizer,
                                   TrainingArguments, Trainer, DataCollatorForLanguageModeling)
        from peft import LoraConfig, get_peft_model

        tok = AutoTokenizer.from_pretrained(self.repo)
        tok.pad_token = tok.pad_token or tok.eos_token

        def load(path):
            rows = [json.loads(l) for l in Path(path).read_text().splitlines()]
            texts = [r["prompt"] + r["completion"] + tok.eos_token for r in rows]
            enc = tok(texts, truncation=True, max_length=1024, padding="max_length")
            return Dataset.from_dict(enc)

        train_ds, valid_ds = load(train_jsonl), load(valid_jsonl)
        model = AutoModelForCausalLM.from_pretrained(self.repo, torch_dtype=torch.float16, device_map="auto")
        model = get_peft_model(model, LoraConfig(r=self.lora_rank, lora_alpha=32,
                               task_type="CAUSAL_LM", target_modules="all-linear"))
        args = TrainingArguments(output_dir=str(adapter_out), num_train_epochs=self.epochs,
                                 per_device_train_batch_size=self.batch_size,
                                 learning_rate=self.learning_rate, logging_steps=10, save_strategy="epoch")
        Trainer(model=model, args=args, train_dataset=train_ds, eval_dataset=valid_ds,
                data_collator=DataCollatorForLanguageModeling(tok, mlm=False)).train()
        model.save_pretrained(str(adapter_out))
        return Path(adapter_out)
