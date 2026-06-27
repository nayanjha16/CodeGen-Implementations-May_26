from pathlib import Path

class Seq2SeqTrainer:
    """LoRA fine-tuning for encoder-decoder models (CodeT5+) via HF PEFT.

    Unlike HFTrainer (causal: prompt+completion concatenated), here the prompt is
    the *encoder* input and the completion is the *decoder* target (labels), so
    there is no causal concatenation. Loads the patched tokenizer (tokenizer_repo)
    when given — the same sentinel-stripped copy HFSeq2SeqRunner uses to dodge the
    transformers-5 legacy-sentinel breakage. float32 (T5 is fp16-unstable on MPS).
    """

    def __init__(self, repo: str, tokenizer_repo: str | None = None, lora_rank: int = 16,
                 epochs: int = 3, batch_size: int = 4, learning_rate: float = 2e-4,
                 max_in: int = 512, max_out: int = 256):
        self.repo = repo
        self.tokenizer_repo = tokenizer_repo
        self.lora_rank = lora_rank
        self.epochs = epochs
        self.batch_size = batch_size
        self.learning_rate = learning_rate
        self.max_in = max_in
        self.max_out = max_out

    def train(self, train_jsonl: Path, valid_jsonl: Path, adapter_out: Path) -> Path:
        import json
        import torch
        from datasets import Dataset
        from transformers import (AutoModelForSeq2SeqLM, AutoTokenizer,
                                   Seq2SeqTrainingArguments,
                                   Seq2SeqTrainer as HFSeq2SeqTrainer,
                                   DataCollatorForSeq2Seq)
        from peft import LoraConfig, get_peft_model

        tok = AutoTokenizer.from_pretrained(self.tokenizer_repo or self.repo)
        tok.truncation_side = "left"  # keep the question at the prompt tail

        def load(path):
            rows = [json.loads(l) for l in Path(path).read_text().splitlines() if l.strip()]
            enc = tok([r["prompt"] for r in rows], truncation=True, max_length=self.max_in)
            labels = tok(text_target=[r["completion"] for r in rows],
                         truncation=True, max_length=self.max_out)
            enc["labels"] = labels["input_ids"]
            return Dataset.from_dict(enc)

        train_ds, valid_ds = load(train_jsonl), load(valid_jsonl)
        model = AutoModelForSeq2SeqLM.from_pretrained(self.repo, torch_dtype=torch.float32)
        model = get_peft_model(model, LoraConfig(r=self.lora_rank, lora_alpha=32,
                               task_type="SEQ_2_SEQ_LM", target_modules="all-linear"))
        args = Seq2SeqTrainingArguments(
            output_dir=str(adapter_out), num_train_epochs=self.epochs,
            per_device_train_batch_size=self.batch_size, learning_rate=self.learning_rate,
            logging_steps=10, save_strategy="epoch", report_to=[])
        HFSeq2SeqTrainer(model=model, args=args, train_dataset=train_ds, eval_dataset=valid_ds,
                         data_collator=DataCollatorForSeq2Seq(tok, model=model)).train()
        model.save_pretrained(str(adapter_out))
        return Path(adapter_out)
