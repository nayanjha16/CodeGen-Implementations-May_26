"""Quick training-throughput benchmark. Runs a handful of steps and reports
seconds/step + peak GPU memory for a given seq length / grad-checkpoint
setting. Works on CUDA (Colab), MPS (Mac) or CPU. Temporary diagnostic
script."""

import argparse
import sys
import time
from pathlib import Path

import torch
from datasets import load_from_disk
from transformers import AutoModelForCausalLM, AutoTokenizer
from trl import SFTConfig, SFTTrainer
from transformers import TrainerCallback

PROJECT_ROOT = Path(__file__).resolve().parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from utils.device import get_best_device, get_training_precision

MODEL = "Qwen/Qwen2.5-Coder-0.5B-Instruct"
DATA = PROJECT_ROOT / "data" / "processed" / "java2py_avatar" / "train"


def _peak_memory_gb(device: str) -> float:
    """Peak allocated device memory in GB, or NaN when unavailable."""
    try:
        if device == "cuda":
            return torch.cuda.max_memory_allocated() / 1e9
        if device == "mps":
            return torch.mps.driver_allocated_memory() / 1e9
    except Exception:
        pass
    return float("nan")


class StepTimer(TrainerCallback):
    def __init__(self, warmup=1):
        self.warmup = warmup
        self.times = []
        self._t = None

    def on_step_begin(self, args, state, control, **kw):
        self._t = time.time()

    def on_step_end(self, args, state, control, **kw):
        if self._t is not None:
            self.times.append(time.time() - self._t)


def run(seq_len: int, grad_ckpt: bool, max_steps: int, batch: int, grad_accum: int):
    device = get_best_device("auto")
    precision = get_training_precision(device)
    model_dtype = torch.bfloat16 if precision["bf16"] else (
        torch.float16 if precision["fp16"] else torch.float32
    )

    tok = AutoTokenizer.from_pretrained(MODEL, trust_remote_code=True)
    if tok.pad_token is None:
        tok.pad_token = tok.eos_token

    model = AutoModelForCausalLM.from_pretrained(
        MODEL, trust_remote_code=True, torch_dtype=model_dtype
    )
    if device != "cpu":
        model = model.to(device)

    from peft import LoraConfig, get_peft_model, TaskType

    lora = LoraConfig(
        r=16, lora_alpha=32, lora_dropout=0.05, bias="none",
        task_type=TaskType.CAUSAL_LM,
        target_modules=["q_proj", "k_proj", "v_proj", "o_proj",
                        "gate_proj", "up_proj", "down_proj"],
    )
    model = get_peft_model(model, lora)
    if grad_ckpt:
        model.enable_input_require_grads()
        model.gradient_checkpointing_enable(gradient_checkpointing_kwargs={"use_reentrant": False})

    ds = load_from_disk(str(DATA)).select(range(batch * grad_accum * max_steps + 8))

    args = SFTConfig(
        output_dir=str(PROJECT_ROOT / "models" / "_bench_tmp"),
        per_device_train_batch_size=batch,
        gradient_accumulation_steps=grad_accum,
        max_steps=max_steps,
        learning_rate=2e-4,
        bf16=precision["bf16"], fp16=precision["fp16"], use_cpu=(device == "cpu"),
        logging_steps=1, report_to="none",
        max_length=seq_len, dataset_text_field="text",
        gradient_checkpointing=grad_ckpt,
        gradient_checkpointing_kwargs={"use_reentrant": False} if grad_ckpt else None,
        dataloader_pin_memory=False,
        save_strategy="no",
    )
    timer = StepTimer()
    trainer = SFTTrainer(model=model, args=args, train_dataset=ds,
                         processing_class=tok, callbacks=[timer])
    t0 = time.time()
    trainer.train()
    total = time.time() - t0

    steps = timer.times[1:] or timer.times  # drop warmup step
    avg = sum(steps) / len(steps) if steps else float("nan")
    peak = _peak_memory_gb(device)
    print(f"\n=== device={device} seq_len={seq_len} grad_ckpt={grad_ckpt} batch={batch} "
          f"grad_accum={grad_accum} ===")
    print(f"steps timed: {len(steps)} | avg s/optimizer-step: {avg:.2f} "
          f"| total: {total:.1f}s | {device} alloc: {peak:.2f} GB")
    return avg


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--seq", type=int, default=512)
    p.add_argument("--ckpt", action="store_true")
    p.add_argument("--steps", type=int, default=3)
    p.add_argument("--batch", type=int, default=4)
    p.add_argument("--accum", type=int, default=2)
    a = p.parse_args()
    run(a.seq, a.ckpt, a.steps, a.batch, a.accum)
