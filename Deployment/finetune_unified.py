"""Unified LoRA fine-tuning — Pass 1 and Pass 2 (plan §3, §8; SPEC §10 steps 9, 13).

Pass 1 trains the multi-task student on **Stage A** samples (draft-only) across
all three tasks. Pass 2 (``--pass 2 --arm {control,teacher}``) resumes from
Pass 1 and adds **Stage B** revise samples for the mined failures — the two arms
differ only in the analysis string (control = neutral fixed; teacher = diagnosis).

Correctness-critical mechanics enforced here:
- **Loss on completion tokens only** — prompt tokens are masked with ``-100``; the
  unmasked-label fraction on a sample batch is logged (plan §3).
- **Task balance by loss-weighting, NOT upsampling** — every example is seen once;
  each task's per-example loss is scaled so the three contribute ≈1:1:1 gradient
  influence (weights ≈1.0/1.73/1.73). The effective per-task weights are logged
  (SPEC-REVIEW #4; SPEC §10 step 9). No NoSQL example is duplicated.
- **Determinism** — all RNGs seeded from ``config.SEED`` and logged; device+dtype
  logged at startup; MPS→CPU fallback enabled and flagged.

Run:
    python finetune_unified.py --pass 1 [--limit N] [--sanity]
    python finetune_unified.py --pass 2 --arm control [--sanity]
    python finetune_unified.py --pass 2 --arm teacher [--sanity]
"""

from __future__ import annotations

import argparse
import json
import logging
import random

import numpy as np
import torch
from torch.nn import CrossEntropyLoss
from transformers import EarlyStoppingCallback, Trainer, TrainerCallback, TrainingArguments, set_seed

from src import config, loader, splits
from src import model_factory as mf
from src.device import describe, enable_mps_cpu_fallback
from src.logger import setup_logging
from src.prompt_builder import build_training_text
from src.retriever import get_retriever

log = logging.getLogger(__name__)

# Control arm's fixed, information-free analysis (Pass 2). It gives the control the
# same two-stage *shape* as the teacher arm without any diagnostic content, so the
# only thing that differs between arms B and C is the teacher signal (SPEC §6.4).
NEUTRAL_ANALYSIS = "Compare the draft to the schema and question, then correct it."

# Fixed analysis for KEEP examples (correct drafts). Identical across both arms — it
# teaches the model to leave an already-correct draft alone instead of over-correcting
# it (run #1 finding). See build_stage_b_samples.
KEEP_ANALYSIS = "The draft is already correct; keep it."


# --- Reproducibility -------------------------------------------------------
def seed_everything(seed: int) -> None:
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    set_seed(seed)
    log.info("seeded all RNGs with %d", seed)


# --- Task loss weights (loss-weighting, not upsampling) --------------------
def task_weights(counts: dict[str, int]) -> dict[str, float]:
    """Per-task loss weight so each task contributes equal gradient influence.

    Anchored to text2sql = 1.0; weight_t = count_ref / count_t (SPEC-REVIEW #4).
    """
    ref = counts.get("text2sql") or max(counts.values())
    return {t: (ref / c if c else 0.0) for t, c in counts.items()}


# --- Dataset construction --------------------------------------------------
def _encode(prompt: str, full: str, tokenizer) -> tuple[list[int], list[int]]:
    """Tokenize and mask the prompt span (loss on completion only).

    The completion (gold + EOS) is NEVER truncated: if prompt+target exceeds
    max_len we drop the *earliest* prompt tokens (reference block / schema head),
    keeping the always-terminal ``### SYSTEM RESPONSE ###`` cue and the whole
    target. Truncating the target instead would corrupt the label a fine-tune
    exists to learn (matters for the ~1.5% of long-schema examples at max_len 768).
    """
    max_len = config.CONFIG.model.max_len
    target = full[len(prompt):]
    prompt_ids = tokenizer(prompt, add_special_tokens=False)["input_ids"]
    target_ids = tokenizer(target, add_special_tokens=False)["input_ids"] + [tokenizer.eos_token_id]

    room = max_len - len(target_ids)
    if room < 0:  # pathological: target alone longer than max_len — clip target as last resort
        target_ids = target_ids[:max_len]
        prompt_ids = []
    elif len(prompt_ids) > room:
        prompt_ids = prompt_ids[-room:]  # keep the most recent prompt context (incl. response cue)

    input_ids = prompt_ids + target_ids
    labels = [-100] * len(prompt_ids) + target_ids
    return input_ids, labels


def _maybe_reference(ex, rng, use_rag, retrievers):
    """A self-excluded RAG reference for ``ex`` with the 20% no-reference holdout."""
    if not use_rag or rng.random() < config.CONFIG.rag.no_reference_fraction:
        return None
    r = retrievers.get(ex.task) or retrievers.setdefault(ex.task, get_retriever(ex.task))
    refs = r.retrieve_for(ex, top_k=1)
    return refs[0] if refs else None


def build_stage_a_samples(examples, tokenizer, rng, use_rag=True):
    """Stage-A (draft-only) training rows with RAG references (self-excluded)."""
    rows = []
    retrievers = {}
    for ex in examples:
        reference = _maybe_reference(ex, rng, use_rag, retrievers)
        prompt, full = build_training_text(ex, reference=reference)
        input_ids, labels = _encode(prompt, full, tokenizer)
        rows.append({"input_ids": input_ids, "labels": labels, "task": ex.task})
    return rows


def _example_from_record(rec) -> loader.Example:
    """Reconstruct a full Example (incl. schema) from an augmented/failure record."""
    task, db_id = rec["task"], rec["db_id"]
    schema = (loader.load_sql_schema_map() if task == "text2sql"
              else loader.load_nosql_schema_map()).get(db_id, "")
    return loader.Example(
        task=task, source=("spider" if task == "text2sql" else "docspider"),
        split="train", db_id=db_id, question=rec.get("question"),
        source_sql=rec.get("source_sql"), gold=rec["gold"], schema=schema,
        difficulty=None, origin_index=-1, aux_sql=rec.get("aux_sql"),
    )


def build_stage_b_samples(arm, tokenizer, rng, use_rag=True):
    """Stage-B (revise) rows: FIX examples (broken drafts) + KEEP examples (correct drafts).

    Two kinds of revise supervision:
    - **FIX** — the teacher-augmented failures. Both arms share the SAME failure set;
      only the analysis slot differs (control=neutral, teacher=diagnosis). The one
      experimental variable (plan §8, SPEC §6.4).
    - **KEEP** — correct Pass-1 drafts, target = the draft itself, analysis fixed to
      ``KEEP_ANALYSIS``, **identical across both arms**. Added after run #1 showed the
      revise pass over-corrects (it broke more correct drafts than it fixed) because
      Stage-B had only broken drafts. KEEP teaches "if the draft is right, keep it."
      Balanced ~1:1 with FIX per task; identical in both arms so the C−B contrast stays
      clean (the only arm difference remains the FIX analysis slot).
    """
    rows = []
    retrievers = {}
    keep_rng = random.Random(config.SEED + 7)
    for task in config.TASKS:
        aug_path = config.AUGMENTED_DIR / f"{task}_augmented.json"
        if not aug_path.exists():
            continue
        fix_recs = json.loads(aug_path.read_text(encoding="utf-8"))
        for rec in fix_recs:
            ex = _example_from_record(rec)
            reference = _maybe_reference(ex, rng, use_rag, retrievers)
            analysis = NEUTRAL_ANALYSIS if arm == "control" else rec["teacher_analysis"]
            prompt, full = build_training_text(
                ex, reference=reference, broken_draft=rec["broken_draft"], analysis=analysis)
            input_ids, labels = _encode(prompt, full, tokenizer)
            rows.append({"input_ids": input_ids, "labels": labels, "task": task})

        # KEEP examples: sample ~1:1 with the FIX count for this task. These are the
        # run #2 "final version" fix; without them Stage-B degrades to run #1's FIX-only
        # training (the revise pass over-corrects). Their absence is therefore a silent
        # regression to a SUPERSEDED result — warn loudly rather than skip quietly, per
        # the project's no-silent-anything rule.
        correct_path = config.FAILURES_DIR / f"{task}_correct.json"
        pool = json.loads(correct_path.read_text(encoding="utf-8")) if correct_path.exists() else []
        if not pool:
            log.warning(
                "Stage-B %s: NO KEEP pool (%s missing/empty) -> Stage-B is FIX-only, "
                "reproducing the SUPERSEDED run #1 over-correction (not the run #2 final "
                "version). Run extract_failures.py so %s_correct.json is populated.",
                task, correct_path, task)
            continue
        n_keep = min(len(fix_recs), len(pool))
        for rec in keep_rng.sample(pool, n_keep):
            keep_rec = {**rec, "gold": rec["draft"]}  # target IS the correct draft (echo it)
            ex = _example_from_record(keep_rec)
            reference = _maybe_reference(ex, rng, use_rag, retrievers)
            prompt, full = build_training_text(
                ex, reference=reference, broken_draft=rec["draft"], analysis=KEEP_ANALYSIS)
            input_ids, labels = _encode(prompt, full, tokenizer)
            rows.append({"input_ids": input_ids, "labels": labels, "task": task})
        log.info("Stage-B %s: fix=%d keep=%d (arm=%s)", task, len(fix_recs), n_keep, arm)
    return rows


def attach_weights(rows, weights: dict[str, float]):
    for r in rows:
        r["weight"] = float(weights[r["task"]])
    return rows


def log_unmasked_fraction(rows, sample: int = 64) -> float:
    """Log the fraction of non-masked labels over a sample (should be small)."""
    subset = rows[:sample]
    total = sum(len(r["labels"]) for r in subset)
    unmasked = sum(sum(1 for x in r["labels"] if x != -100) for r in subset)
    frac = unmasked / max(total, 1)
    log.info("unmasked-label fraction on %d-sample batch: %.3f (loss is completion-only)", len(subset), frac)
    return frac


# --- Collator --------------------------------------------------------------
class Collator:
    """Pad input_ids/labels (labels with -100) and stack per-example weights."""

    def __init__(self, pad_id: int):
        self.pad_id = pad_id

    def __call__(self, features):
        maxlen = max(len(f["input_ids"]) for f in features)
        input_ids, attn, labels, weights = [], [], [], []
        for f in features:
            ids = f["input_ids"]
            pad = maxlen - len(ids)
            input_ids.append(ids + [self.pad_id] * pad)
            attn.append([1] * len(ids) + [0] * pad)
            labels.append(f["labels"] + [-100] * pad)
            weights.append(f["weight"])
        return {
            "input_ids": torch.tensor(input_ids, dtype=torch.long),
            "attention_mask": torch.tensor(attn, dtype=torch.long),
            "labels": torch.tensor(labels, dtype=torch.long),
            "weight": torch.tensor(weights, dtype=torch.float32),
        }


# --- Weighted, masked-loss Trainer -----------------------------------------
class MPSCacheCallback(TrainerCallback):
    """Empty the MPS allocator cache periodically so long runs don't creep into swap."""

    def __init__(self, every: int = 20):
        self.every = every

    def on_step_end(self, args, state, control, **kwargs):
        if state.global_step % self.every == 0 and torch.backends.mps.is_available():
            torch.mps.empty_cache()


class WeightedTrainer(Trainer):
    """Cross-entropy on completion tokens, scaled per-example by task weight."""

    def compute_loss(self, model, inputs, return_outputs=False, **kwargs):
        weights = inputs.pop("weight")
        labels = inputs.pop("labels")
        outputs = model(**inputs)
        logits = outputs.logits

        shift_logits = logits[:, :-1, :].contiguous()
        shift_labels = labels[:, 1:].contiguous()
        loss_fct = CrossEntropyLoss(reduction="none", ignore_index=-100)
        b, t = shift_labels.shape
        tok_loss = loss_fct(shift_logits.reshape(b * t, -1).float(), shift_labels.reshape(b * t)).reshape(b, t)
        valid = (shift_labels != -100).float()
        per_ex = (tok_loss * valid).sum(1) / valid.sum(1).clamp(min=1.0)
        loss = (per_ex * weights.to(per_ex.device)).mean()
        return (loss, outputs) if return_outputs else loss


# --- Data assembly per pass ------------------------------------------------
def load_split_examples(limit: int | None):
    """Train + valid partitions for all 3 tasks (dev is never loaded here)."""
    train_all, valid_all = [], []
    for task in config.TASKS:
        exs = loader.load_task(task, "train")
        name = "spider" if task == "text2sql" else task
        tr, va = splits.carve_valid(exs, name)
        if limit is not None:
            tr, va = tr[: limit], va[: max(2, limit // 5)]
        train_all += tr
        valid_all += va
    return train_all, valid_all


def build_datasets(pass_num: int, arm: str | None, limit: int | None, tokenizer, use_rag: bool):
    rng = random.Random(config.SEED)
    train_ex, valid_ex = load_split_examples(limit)

    counts = {t: sum(1 for e in train_ex if e.task == t) for t in config.TASKS}
    weights = task_weights(counts)
    log.info("train counts per task: %s", counts)
    log.info("effective per-task loss weights (loss-weighting, not upsampling): "
             "%s", {t: round(w, 3) for t, w in weights.items()})

    train_rows = build_stage_a_samples(train_ex, tokenizer, rng, use_rag=use_rag)
    valid_rows = build_stage_a_samples(valid_ex, tokenizer, random.Random(config.SEED + 1), use_rag=use_rag)

    if pass_num == 2:
        # Add Stage-B revise rows from the teacher-augmented failures. Both arms use
        # the same failures; only the analysis slot differs (control vs teacher).
        stage_b = build_stage_b_samples(arm, tokenizer, random.Random(config.SEED + 2), use_rag=use_rag)
        if not stage_b:
            raise SystemExit("no augmented failures on disk — run generate_teacher_data.py first")
        log.info("pass 2 arm=%s: Stage-A rows=%d + Stage-B rows=%d", arm, len(train_rows), len(stage_b))
        train_rows = train_rows + stage_b

    attach_weights(train_rows, weights)
    attach_weights(valid_rows, weights)
    log_unmasked_fraction(train_rows)
    return train_rows, valid_rows


# --- Training --------------------------------------------------------------
def train(pass_num: int, arm: str | None, limit: int | None, sanity: bool, use_rag: bool):
    seed_everything(config.SEED)
    enable_mps_cpu_fallback()
    log.info("startup: %s", describe())

    tokenizer = mf.load_tokenizer()

    if pass_num == 1:
        model = mf.create_model()
        out_dir = config.PASS1_DIR
    else:
        arm_dir = {"control": config.PASS2_CONTROL_DIR, "teacher": config.PASS2_TEACHER_DIR}[arm]
        model = mf.load_adapter(config.PASS1_DIR, trainable=True)  # resume from Pass 1
        out_dir = arm_dir

    train_rows, valid_rows = build_datasets(pass_num, arm, limit, tokenizer, use_rag)
    log.info("dataset: train=%d valid=%d rows", len(train_rows), len(valid_rows))

    tc = config.CONFIG.train
    epochs = 1 if sanity else tc.epochs_max
    lr = tc.lr_pass1 if pass_num == 1 else tc.lr_pass2

    args = TrainingArguments(
        output_dir=str(out_dir),
        num_train_epochs=epochs,
        per_device_train_batch_size=2 if sanity else tc.batch_size,
        per_device_eval_batch_size=2 if sanity else tc.batch_size,
        gradient_accumulation_steps=1 if sanity else tc.grad_accum,
        learning_rate=lr,
        warmup_ratio=tc.warmup_ratio,
        weight_decay=tc.weight_decay,
        eval_strategy="epoch",
        save_strategy="epoch",
        save_total_limit=2,
        load_best_model_at_end=tc.load_best_model_at_end,
        metric_for_best_model="eval_loss",
        greater_is_better=False,
        logging_steps=10,
        seed=config.SEED,
        report_to=[],
        remove_unused_columns=False,  # keep our "weight"/"task" columns
        label_names=["labels"],
        dataloader_pin_memory=False,   # unsupported on MPS; avoids a warning + overhead
        dataloader_num_workers=0,
        # CRITICAL on MPS with a large-vocab model (Qwen vocab=151936): without this,
        # eval gathers/concatenates the full logits over the whole valid set (hundreds
        # of GB) → swap death-spiral. We only need eval_loss for early-stopping/best-model,
        # so never materialise logits. Does NOT change training or the eval_loss value.
        prediction_loss_only=True,
    )

    callbacks = [MPSCacheCallback(every=10)]
    if tc.early_stopping and not sanity:
        callbacks.append(EarlyStoppingCallback(early_stopping_patience=2))

    trainer = WeightedTrainer(
        model=model,
        args=args,
        train_dataset=train_rows,
        eval_dataset=valid_rows,
        data_collator=Collator(tokenizer.pad_token_id),
        callbacks=callbacks,
    )

    log.info("starting training: pass=%d arm=%s epochs=%d lr=%g", pass_num, arm, epochs, lr)
    trainer.train()

    out_dir.mkdir(parents=True, exist_ok=True)
    model.save_pretrained(str(out_dir))
    tokenizer.save_pretrained(str(out_dir))
    log.info("saved adapter -> %s", out_dir)
    print(f"pass {pass_num}{'/' + arm if arm else ''} done -> {out_dir}")


def main() -> None:
    ap = argparse.ArgumentParser(description="Unified LoRA fine-tuning (Pass 1 / Pass 2).")
    ap.add_argument("--pass", dest="pass_num", type=int, choices=(1, 2), required=True)
    ap.add_argument("--arm", choices=("control", "teacher"), help="required for --pass 2")
    ap.add_argument("--limit", type=int, default=None, help="cap examples per task")
    ap.add_argument("--sanity", action="store_true", help="tiny end-to-end smoke run")
    ap.add_argument("--no_rag", action="store_true", help="disable RAG references in training data")
    args = ap.parse_args()

    if args.pass_num == 2 and not args.arm:
        ap.error("--pass 2 requires --arm {control,teacher}")

    setup_logging(f"finetune_pass{args.pass_num}{'_' + args.arm if args.arm else ''}")
    limit = 24 if args.sanity and args.limit is None else args.limit
    train(args.pass_num, args.arm, limit, args.sanity, use_rag=not args.no_rag)


if __name__ == "__main__":
    main()
