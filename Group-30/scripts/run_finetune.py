"""Stage-1 LoRA fine-tune of codegen-350M-mono on MBPP, formatted to match
HumanEval's continuation shape (signature + docstring -> body).

Run in Colab with a GPU:
    pip install -q transformers==4.44.2 peft==0.13.2 accelerate==0.34.2 datasets==2.21.0
    pip uninstall -y torchao          # avoids a peft<->torchao version clash on Colab
    python Group-30/scripts/run_finetune.py

Produces a LoRA adapter at Group-30/models/lora_mbpp_v2/.
Eval it with run_real_baseline.py's helpers (see the report notes) to compare vs the
0.111 baseline. Measured lift: pass@1 0.111 -> 0.121, pass@5 0.177 -> 0.207 (seed 1234).
"""
import os, re
import torch
from datasets import load_dataset, Dataset
from transformers import (AutoTokenizer, AutoModelForCausalLM, TrainingArguments,
                          Trainer, DataCollatorForSeq2Seq)
from peft import LoraConfig, get_peft_model

MODEL   = "Salesforce/codegen-350M-mono"
MAX_LEN = 512
HERE    = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))   # Group-30/
OUT_DIR = os.path.join(HERE, "models", "lora_mbpp_v2")


def get_func_name(test_list):
    """Recover the target function name from the test asserts."""
    for t in test_list:
        m = re.search(r'assert\s+(?:not\s+)?([A-Za-z_]\w*)\s*\(', t)
        if m:
            return m.group(1)
    return None


def make_continuation(ex):
    """Reshape an MBPP row into HumanEval continuation form.

    PROMPT (loss-masked):  def name(args):\n    \"\"\"<intent>\"\"\"\n
    COMPLETION (learned):  <indented function body>
    Returns None for multi-function / helper-class solutions we can't cleanly split.
    """
    name = get_func_name(ex["test_list"])
    if not name:
        return None
    code = ex["code"].strip()
    if not re.match(rf'def\s+{re.escape(name)}\s*\(', code):   # must start with the target def
        return None
    first_nl = code.find("\n")
    if first_nl == -1:
        return None
    signature = code[:first_nl].rstrip()
    if not signature.endswith(":"):                           # skip rare multi-line headers
        return None
    body = code[first_nl + 1:]
    docstring = f'    """\n    {ex["text"].strip()}\n    """\n'
    return signature + "\n" + docstring, body + "\n"


def main():
    tok = AutoTokenizer.from_pretrained(MODEL)
    tok.pad_token = tok.eos_token

    mbpp = load_dataset("google-research-datasets/mbpp", split="train")
    pairs = [p for p in (make_continuation(ex) for ex in mbpp) if p is not None]
    print(f"Reformatted {len(pairs)}/{len(mbpp)} MBPP examples into HumanEval shape")

    def tok_pair(p):
        prompt, completion = p
        p_ids = tok(prompt, add_special_tokens=False)["input_ids"]
        c_ids = tok(completion, add_special_tokens=False)["input_ids"] + [tok.eos_token_id]
        input_ids = (p_ids + c_ids)[:MAX_LEN]
        labels    = ([-100] * len(p_ids) + c_ids)[:MAX_LEN]   # mask the prompt
        return {"input_ids": input_ids, "labels": labels,
                "attention_mask": [1] * len(input_ids)}

    ds = Dataset.from_list([tok_pair(p) for p in pairs])

    model = AutoModelForCausalLM.from_pretrained(MODEL, torch_dtype=torch.float16)
    model.config.pad_token_id = tok.pad_token_id
    model = get_peft_model(model, LoraConfig(
        r=16, lora_alpha=32, lora_dropout=0.05, bias="none",
        task_type="CAUSAL_LM", target_modules=["qkv_proj", "out_proj"]))
    model.print_trainable_parameters()

    args = TrainingArguments(
        output_dir="/content/lora_out2", num_train_epochs=3,
        per_device_train_batch_size=4, gradient_accumulation_steps=4,
        learning_rate=2e-4, warmup_ratio=0.03, fp16=True,
        logging_steps=5, save_strategy="no", report_to="none")

    Trainer(model=model, args=args, train_dataset=ds,
            data_collator=DataCollatorForSeq2Seq(tok, padding=True,
                                                  label_pad_token_id=-100)).train()

    os.makedirs(OUT_DIR, exist_ok=True)
    model.save_pretrained(OUT_DIR)
    tok.save_pretrained(OUT_DIR)
    print(f"\n✅ LoRA adapter saved to {OUT_DIR}")


if __name__ == "__main__":
    main()
