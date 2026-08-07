"""
Fine-tune CodeGen-350M-Multi using a Unified Multi-Task Framework.
Combines Spider (with Teacher Calibration) and DocSpider (SQL-to-NoSQL & Text-to-NoSQL).

Usage:
    python finetune_unified.py
"""

import argparse
import os
import random
import torch
import numpy as np
import re
import transformers
import datasets as _ds_lib
from datasets import Dataset
from transformers import (
    TrainingArguments,
    Trainer,
    DataCollatorForSeq2Seq,
)

# Suppress INFO-level chatter from HuggingFace libraries — model-load messages,
# tokenizer warnings, dataset map progress — all go to log file via pipeline_logger.
transformers.logging.set_verbosity_warning()
_ds_lib.logging.set_verbosity_warning()

# Environment hooks
from src.config import MODELS, DATA, get_device_settings
from src.model_factory import load_model
from src.loader import (
    load_spider_tasks, load_spider_compact_schema_maps_with_fk, load_spider_table_names_map,
    load_docspider_tasks, load_schema_context_map, load_spider_fk_neighbors_map,
)
from src.prompt_builder import build_text2sql_sample, build_sql2nosql_sample, build_text2nosql_sample
from src.logger import pipeline_logger



def minify_nosql_schema(schema_obj) -> str:
    """
    Safely compresses MongoDB / DocSpider schema objects (JSON dicts or text structures)
    by flattening collections inline and stripping excessive formatting whitespaces.
    """
    if not schema_obj:
        return ""

    # If the loader returns a raw JSON/Dictionary context map
    if isinstance(schema_obj, dict):
        parts = []
        for collection, fields in schema_obj.items():
            if isinstance(fields, list):
                field_str = ", ".join(str(f) for f in fields)
            elif isinstance(fields, dict):
                field_str = ", ".join(str(k) for k in fields.keys())
            else:
                field_str = str(fields)
            parts.append(f"{collection}({field_str})")
        return " | ".join(parts)

    # If the loader returns a string representation
    elif isinstance(schema_obj, str):
        return re.sub(r'\s+', ' ', schema_obj).strip()

    return str(schema_obj)


def _build_unified_dataset(spider_tasks, docspider_tasks, spider_schemas, docspider_schemas, tokenizer, max_len, no_rag=False, schema_pruner=None):
    samples = []

    # ------------------------------------------------------------------ #
    # Schema minification
    # ------------------------------------------------------------------ #
    pipeline_logger.info("fine_tuning", "schema_minification_start", stats={
        "spider_dbs": len(spider_schemas),
        "docspider_dbs": len(docspider_schemas)
    })
    print("✂️ Compressing multi-dialect schema objects into inline tokens...")
    minified_spider = spider_schemas  # already compact with FK annotations from loader
    minified_docspider = {db: minify_nosql_schema(ctx) for db, ctx in docspider_schemas.items()}
    pipeline_logger.info("fine_tuning", "schema_minification_done", stats={
        "spider_dbs_minified": len(minified_spider),
        "docspider_dbs_minified": len(minified_docspider)
    })

    # ------------------------------------------------------------------ #
    # Task count balancing
    # ------------------------------------------------------------------ #
    target_count = len(spider_tasks)
    oversampled_docspider = random.choices(docspider_tasks, k=target_count)
    pipeline_logger.info("fine_tuning", "task_balancing", stats={
        "spider_count": len(spider_tasks),
        "docspider_original": len(docspider_tasks),
        "docspider_oversampled": len(oversampled_docspider),
        "target_count": target_count
    })

    # ------------------------------------------------------------------ #
    # Pass mode detection
    # ------------------------------------------------------------------ #
    # Detect Pass 2 by scanning all spider samples — not just the first —
    # so mixed datasets (some failures with teacher data, rest without) are handled correctly.
    has_teacher_data = any(
        "broken_draft" in t
        and t.get("broken_draft", "") not in ("", "SELECT * FROM fallback;")
        for t in spider_tasks
    )
    pipeline_logger.info("fine_tuning", "pass_mode_detected", stats={
        "has_teacher_data": has_teacher_data,
        "mode": "Pass 2 (Teacher Calibration)" if has_teacher_data else "Pass 1 (Standard)"
    })

    if has_teacher_data:
        print("🧠 Teacher data detected. Compiling context using Correction-Based Calibration formatting (Pass 2).")
    else:
        print("🎯 Standard target formatting activated. Omitting fallback boilerplate blocks (Pass 1).")

    # ------------------------------------------------------------------ #
    # Semantic RAG — load retrieval indices built by build_retrieval_index.py.
    # Falls back to random selection if the index has not been built yet.
    # ------------------------------------------------------------------ #
    use_semantic_rag = False
    text2sql_retriever = sql2nosql_retriever = text2nosql_retriever = None
    spider_table_names_map = {}
    if no_rag:
        pipeline_logger.info("fine_tuning", "rag_disabled", stats={"reason": "--no_rag flag set"})
        print("⛔ RAG disabled — training without reference examples.")
    else:
        try:
            from src.retriever import Retriever
            text2sql_retriever  = Retriever(task="text2sql")
            sql2nosql_retriever = Retriever(task="sql2nosql")
            text2nosql_retriever = Retriever(task="text2nosql")
            spider_table_names_map = load_spider_table_names_map()
            use_semantic_rag = True
            pipeline_logger.info("fine_tuning", "semantic_rag_loaded", stats={"status": "ok"})
            print("🔍 Semantic retrieval index loaded — using similar examples for training RAG.")
        except Exception as _rag_err:
            pipeline_logger.warning("fine_tuning", "semantic_rag_unavailable", stats={"error": str(_rag_err)})
            print(f"⚠️  Retrieval index unavailable ({_rag_err}). Falling back to random RAG examples.")

    # ------------------------------------------------------------------ #
    # 1. Spider Text-to-SQL samples
    # ------------------------------------------------------------------ #
    spider_rag_fallbacks = 0

    for i, entry in enumerate(spider_tasks):
        if no_rag:
            rag_example = None
        elif use_semantic_rag:
            table_names = spider_table_names_map.get(entry["db_id"], [])
            results = text2sql_retriever.retrieve_text2sql(
                entry["question"], entry["db_id"], table_names, k=2
            )
            rag_example = next(
                (r for r in results if r.get("question") != entry["question"]), None
            ) or (results[0] if results else None)
        else:
            rag_pool = [t for t in spider_tasks if t["question"] != entry["question"]]
            rag_example = random.choice(rag_pool) if rag_pool else None

        bd_value = entry.get("broken_draft", None) if has_teacher_data else None
        ta_value = entry.get("teacher_analysis", None) if has_teacher_data else None

        prompt, target = build_text2sql_sample(
            model_type="codegen",
            question=entry["question"],
            db_id=entry["db_id"],
            sql=entry["query"],
            schema_maps=minified_spider,
            broken_draft=bd_value,
            teacher_analysis=ta_value,
            retrieved_example=rag_example,
            skip_rag=False,
            schema_pruner=schema_pruner,
        )

        p_ids = tokenizer.encode(prompt, add_special_tokens=False)
        t_ids = tokenizer.encode(target, add_special_tokens=False) + [tokenizer.eos_token_id]

        rag_fallback = False
        if len(p_ids) + len(t_ids) > max_len and rag_example:
            # Log the overflow before stripping RAG context
            pipeline_logger.warning("fine_tuning", "spider_rag_fallback_triggered", stats={
                "index": i,
                "db_id": entry["db_id"],
                "question": entry["question"][:120],
                "prompt_tokens": len(p_ids),
                "target_tokens": len(t_ids),
                "total_tokens": len(p_ids) + len(t_ids),
                "max_len": max_len
            })
            prompt, target = build_text2sql_sample(
                model_type="codegen",
                question=entry["question"],
                db_id=entry["db_id"],
                sql=entry["query"],
                schema_maps=minified_spider,
                broken_draft=bd_value,
                teacher_analysis=ta_value,
                retrieved_example=rag_example,
                skip_rag=True,
                schema_pruner=schema_pruner,
            )
            rag_fallback = True
            spider_rag_fallbacks += 1

        # Periodic sample logging — every 100th entry shows full prompt + target
        if i % 100 == 0:
            pipeline_logger.record(
                stage="fine_tuning",
                action="spider_sample_preview",
                input_data=prompt,
                output_data=target,
                stats={
                    "index": i,
                    "db_id": entry["db_id"],
                    "question": entry["question"][:120],
                    "prompt_tokens": len(p_ids),
                    "target_tokens": len(t_ids),
                    "rag_fallback": rag_fallback,
                    "has_teacher_data": has_teacher_data
                }
            )

        samples.append((prompt, target))

    pipeline_logger.info("fine_tuning", "spider_samples_built", stats={
        "total_spider_samples": len(spider_tasks),
        "rag_fallbacks": spider_rag_fallbacks,
        "rag_fallback_pct": round(spider_rag_fallbacks / len(spider_tasks) * 100, 2) if spider_tasks else 0
    })

    # ------------------------------------------------------------------ #
    # 2. DocSpider multi-variant samples
    # ------------------------------------------------------------------ #
    docspider_trans_fallbacks = 0
    docspider_dir_fallbacks = 0

    for i, entry in enumerate(oversampled_docspider):
        if no_rag:
            rag_example = None
        elif use_semantic_rag:
            schema_str = minified_docspider.get(entry.get("db_id", ""), "")
            results = text2nosql_retriever.retrieve_text2nosql(
                entry.get("question", ""), entry.get("db_id", ""), schema_str, k=2
            )
            rag_example = next(
                (r for r in results if r.get("question") != entry.get("question")), None
            ) or (results[0] if results else None)
        else:
            rag_pool = [t for t in docspider_tasks if t.get("question") != entry.get("question")]
            rag_example = random.choice(rag_pool) if rag_pool else None

        # --- Phase A: Transpilation (SQL → MQL) ---
        # In Pass 2, per-entry teacher data is stored under broken_draft_trans / teacher_analysis_trans
        bd_trans = entry.get("broken_draft_trans", None)
        ta_trans = entry.get("teacher_analysis_trans", None)

        p_trans, t_trans = build_sql2nosql_sample(
            model_type="codegen",
            sql=entry.get("spider_gold_sql", ""),
            db_id=entry.get("db_id", ""),
            mql=entry.get("query", ""),
            schema_maps=minified_docspider,
            broken_draft=bd_trans,
            teacher_analysis=ta_trans,
            retrieved_example=rag_example,
            skip_rag=False,
            schema_pruner=schema_pruner,
        )

        pa_ids = tokenizer.encode(p_trans, add_special_tokens=False)
        ta_ids = tokenizer.encode(t_trans, add_special_tokens=False) + [tokenizer.eos_token_id]

        trans_rag_fallback = False
        if len(pa_ids) + len(ta_ids) > max_len and rag_example:
            pipeline_logger.warning("fine_tuning", "docspider_trans_rag_fallback_triggered", stats={
                "index": i,
                "db_id": entry.get("db_id"),
                "prompt_tokens": len(pa_ids),
                "target_tokens": len(ta_ids),
                "total_tokens": len(pa_ids) + len(ta_ids),
                "max_len": max_len
            })
            p_trans, t_trans = build_sql2nosql_sample(
                model_type="codegen",
                sql=entry.get("spider_gold_sql", ""),
                db_id=entry.get("db_id", ""),
                mql=entry.get("query", ""),
                schema_maps=minified_docspider,
                broken_draft=bd_trans,
                teacher_analysis=ta_trans,
                retrieved_example=rag_example,
                skip_rag=True,
                schema_pruner=schema_pruner,
            )
            trans_rag_fallback = True
            docspider_trans_fallbacks += 1

        if i % 100 == 0:
            pipeline_logger.record(
                stage="fine_tuning",
                action="docspider_sql2nosql_sample_preview",
                input_data=p_trans,
                output_data=t_trans,
                stats={
                    "index": i,
                    "db_id": entry.get("db_id"),
                    "sql_preview": entry.get("spider_gold_sql", "")[:120],
                    "prompt_tokens": len(pa_ids),
                    "target_tokens": len(ta_ids),
                    "rag_fallback": trans_rag_fallback
                }
            )

        samples.append((p_trans, t_trans))

        # --- Phase B: Direct generation (NL → MQL) ---
        bd_dir = entry.get("broken_draft_dir", None)
        ta_dir = entry.get("teacher_analysis_dir", None)

        p_dir, t_dir = build_text2nosql_sample(
            model_type="codegen",
            question=entry.get("question", ""),
            db_id=entry.get("db_id", ""),
            mql=entry.get("query", ""),
            schema_maps=minified_docspider,
            broken_draft=bd_dir,
            teacher_analysis=ta_dir,
            retrieved_example=rag_example,
            skip_rag=False,
            schema_pruner=schema_pruner,
        )

        pb_ids = tokenizer.encode(p_dir, add_special_tokens=False)
        tb_ids = tokenizer.encode(t_dir, add_special_tokens=False) + [tokenizer.eos_token_id]

        dir_rag_fallback = False
        if len(pb_ids) + len(tb_ids) > max_len and rag_example:
            pipeline_logger.warning("fine_tuning", "docspider_dir_rag_fallback_triggered", stats={
                "index": i,
                "db_id": entry.get("db_id"),
                "question": entry.get("question", "")[:120],
                "prompt_tokens": len(pb_ids),
                "target_tokens": len(tb_ids),
                "total_tokens": len(pb_ids) + len(tb_ids),
                "max_len": max_len
            })
            p_dir, t_dir = build_text2nosql_sample(
                model_type="codegen",
                question=entry.get("question", ""),
                db_id=entry.get("db_id", ""),
                mql=entry.get("query", ""),
                schema_maps=minified_docspider,
                broken_draft=bd_dir,
                teacher_analysis=ta_dir,
                retrieved_example=rag_example,
                skip_rag=True,
                schema_pruner=schema_pruner,
            )
            dir_rag_fallback = True
            docspider_dir_fallbacks += 1

        if i % 100 == 0:
            pipeline_logger.record(
                stage="fine_tuning",
                action="docspider_text2nosql_sample_preview",
                input_data=p_dir,
                output_data=t_dir,
                stats={
                    "index": i,
                    "db_id": entry.get("db_id"),
                    "question": entry.get("question", "")[:120],
                    "prompt_tokens": len(pb_ids),
                    "target_tokens": len(tb_ids),
                    "rag_fallback": dir_rag_fallback
                }
            )

        samples.append((p_dir, t_dir))

    pipeline_logger.info("fine_tuning", "docspider_samples_built", stats={
        "oversampled_entries": len(oversampled_docspider),
        "trans_samples": len(oversampled_docspider),
        "dir_samples": len(oversampled_docspider),
        "trans_rag_fallbacks": docspider_trans_fallbacks,
        "dir_rag_fallbacks": docspider_dir_fallbacks
    })

    random.shuffle(samples)

    # ------------------------------------------------------------------ #
    # 3. Tokenization with hard boundary enforcement
    # ------------------------------------------------------------------ #
    pipeline_logger.info("fine_tuning", "tokenization_start", stats={
        "total_samples": len(samples),
        "max_len": max_len
    })

    tokenized_samples = []
    truncation_count = 0
    total_raw_tokens = 0

    for prompt, target in samples:
        prompt_ids = tokenizer.encode(prompt, add_special_tokens=False)
        target_ids = tokenizer.encode(target, add_special_tokens=False) + [tokenizer.eos_token_id]

        total_len = len(prompt_ids) + len(target_ids)
        total_raw_tokens += total_len

        if total_len > max_len:
            truncation_count += 1
            available_prompt_space = max_len - len(target_ids)
            if available_prompt_space <= 0:
                target_ids = target_ids[:max_len]
                prompt_ids = []
            else:
                prompt_ids = prompt_ids[-available_prompt_space:]

        input_ids = prompt_ids + target_ids
        labels = [-100] * len(prompt_ids) + target_ids

        tokenized_samples.append({"input_ids": input_ids, "labels": labels})

    avg_tokens = total_raw_tokens / len(samples) if samples else 0
    pipeline_logger.info("fine_tuning", "tokenization_complete", stats={
        "total_samples": len(tokenized_samples),
        "truncations": truncation_count,
        "truncation_pct": round(truncation_count / len(samples) * 100, 2) if samples else 0,
        "avg_raw_tokens": round(avg_tokens, 1),
        "max_len_budget": max_len
    })

    return Dataset.from_list(tokenized_samples)


def preprocess_logits_for_metrics(logits, labels):
    # Convert logits → token IDs immediately per batch to avoid storing the
    # full (samples × seq_len × vocab_size) tensor in memory.
    return logits.argmax(dim=-1)


def compute_metrics(eval_pred):
    predictions, labels = eval_pred
    exact_matches = []
    for pred, label in zip(predictions, labels):
        mask = label != -100
        exact_matches.append(np.array_equal(pred[mask], label[mask]))
    return {"exact_match": float(np.mean(exact_matches))}


def main():
    parser = argparse.ArgumentParser(description="Unified CodeGen multi-task fine-tuner")
    parser.add_argument("--spider_data",    default=None, help="Override Spider training JSON path (default: DATA['spider_train'])")
    parser.add_argument("--docspider_data", default=None, help="Override DocSpider training JSON path (default: DATA['docspider_train'])")
    parser.add_argument("--checkpoint_dir", default=None, help="Override checkpoint output directory")
    parser.add_argument("--resume_from",     default=None, help="Path to an existing LoRA checkpoint to continue training from (e.g. Pass 1 checkpoint for Pass 2)")
    parser.add_argument("--resume_training", action="store_true", help="Resume from the latest checkpoint-* inside checkpoint_dir (use after a Colab disconnect)")
    parser.add_argument("--no_rag",          action="store_true", help="Disable RAG examples in training prompts (train zero-shot, no reference examples)")
    parser.add_argument("--limit",          default=None, type=int, help="Cap number of training samples (sanity testing)")
    args = parser.parse_args()

    cfg = MODELS["codegen"]
    dev = get_device_settings()
    checkpoint_path = args.checkpoint_dir or cfg["checkpoint_pass1"]

    os.makedirs(checkpoint_path, exist_ok=True)

    pipeline_logger.info("fine_tuning", "pipeline_start", stats={
        "model_id": cfg["model_id"],
        "epochs": cfg["epochs"],
        "lr": cfg["lr"],
        "train_batch": cfg["train_batch"],
        "grad_accum": cfg["grad_accum"],
        "effective_batch": cfg["train_batch"] * cfg["grad_accum"],
        "max_input_len": cfg.get("max_input_len", 2048),
        "lora_r": cfg["lora_r"],
        "lora_alpha": cfg["lora_alpha"],
        "checkpoint_output": checkpoint_path,
        "resume_from": args.resume_from or "none (fresh LoRA)",
        "device": dev["device"],
        "fp16": dev["codegen_fp16"],
        "bf16": dev["codegen_bf16"]
    })
    print(f"[Unified Pipeline] Initialization Starting for: {cfg['model_id']}")

    # ------------------------------------------------------------------ #
    # Data loading — paths can be overridden via CLI for Pass 2
    # ------------------------------------------------------------------ #
    spider_data_path    = args.spider_data    or DATA["spider_train"]
    docspider_data_path = args.docspider_data or DATA["docspider_train"]

    spider_train    = load_spider_tasks(spider_data_path)
    docspider_train = load_docspider_tasks(docspider_data_path)

    if args.limit:
        spider_train    = spider_train[:args.limit]
        docspider_train = docspider_train[:args.limit]
        pipeline_logger.info("fine_tuning", "limit_applied", stats={"limit": args.limit})
        print(f"[Unified Pipeline] Sanity limit: {args.limit} samples per dataset.")

    pipeline_logger.info("fine_tuning", "datasets_loaded", stats={
        "spider_tasks": len(spider_train),
        "docspider_tasks": len(docspider_train),
        "spider_path": spider_data_path,
        "docspider_path": docspider_data_path
    })

    spider_schemas = load_spider_compact_schema_maps_with_fk()
    docspider_schemas = load_schema_context_map(DATA["docspider_collections"])

    pipeline_logger.info("fine_tuning", "schemas_loaded", stats={
        "spider_dbs": len(spider_schemas),
        "docspider_dbs": len(docspider_schemas)
    })

    # ------------------------------------------------------------------ #
    # Schema pruner — trims each prompt's schema to relevant tables only.
    # Requires the schema index built by:
    #   python scripts/build_retrieval_index.py --task schema
    # Falls back gracefully (full schema) if the index is absent.
    # ------------------------------------------------------------------ #
    schema_pruner = None
    try:
        from src.schema_pruner import SchemaPruner
        fk_neighbors  = load_spider_fk_neighbors_map()
        schema_pruner = SchemaPruner(fk_neighbors=fk_neighbors)
        pipeline_logger.info("fine_tuning", "schema_pruner_loaded", stats={"status": "ok"})
        print("✂️  Schema pruner loaded — irrelevant tables will be trimmed from prompts.")
    except Exception as _prune_err:
        pipeline_logger.warning("fine_tuning", "schema_pruner_unavailable",
                                stats={"error": str(_prune_err)})
        print(f"⚠️  Schema pruner unavailable ({_prune_err}). Using full schemas.")

    # ------------------------------------------------------------------ #
    # Model + tokenizer
    # ------------------------------------------------------------------ #
    # Pass --resume_from to continue from an existing checkpoint (e.g. Pass 1 → Pass 2).
    # If None, fresh LoRA adapters are injected on top of the frozen base model.
    model, tokenizer = load_model("codegen", checkpoint_path=args.resume_from, mode="train")

    # ------------------------------------------------------------------ #
    # Dataset construction
    # ------------------------------------------------------------------ #
    print("[Dataset Linker] Compiling unified data matrix...")
    train_dataset = _build_unified_dataset(
        spider_tasks=spider_train,
        docspider_tasks=docspider_train,
        spider_schemas=spider_schemas,
        docspider_schemas=docspider_schemas,
        tokenizer=tokenizer,
        max_len=cfg.get("max_input_len", 2048),
        no_rag=args.no_rag,
        schema_pruner=schema_pruner,
    )

    pipeline_logger.info("fine_tuning", "dataset_ready", stats={
        "total_samples": len(train_dataset)
    })

    # ------------------------------------------------------------------ #
    # Eval split — 5% of training data, used to select the best epoch
    # Skip if the dataset is too small (e.g. --sanity with 3 samples)
    # ------------------------------------------------------------------ #
    if len(train_dataset) >= 20:
        split       = train_dataset.train_test_split(test_size=0.05, seed=42)
        train_split = split["train"]
        eval_split  = split["test"]
        pipeline_logger.info("fine_tuning", "eval_split_created", stats={
            "train_samples": len(train_split), "eval_samples": len(eval_split)
        })
    else:
        train_split = train_dataset
        eval_split  = None
        pipeline_logger.info("fine_tuning", "eval_split_skipped", stats={"reason": "dataset_too_small"})

    # ------------------------------------------------------------------ #
    # Trainer setup
    # ------------------------------------------------------------------ #
    data_collator = DataCollatorForSeq2Seq(
        tokenizer, pad_to_multiple_of=8, return_tensors="pt", padding=True
    )

    use_eval = eval_split is not None
    training_args = TrainingArguments(
        output_dir                  = checkpoint_path,
        per_device_train_batch_size = cfg["train_batch"],
        per_device_eval_batch_size  = max(1, cfg["train_batch"] * 2),
        gradient_accumulation_steps = cfg["grad_accum"],
        learning_rate               = cfg["lr"],
        num_train_epochs            = cfg["epochs"],
        warmup_ratio                = cfg["warmup_ratio"],
        weight_decay                = cfg["weight_decay"],
        logging_steps               = 200,
        disable_tqdm                = True,
        save_strategy               = "epoch",
        eval_strategy               = "epoch" if use_eval else "no",
        load_best_model_at_end      = use_eval,
        metric_for_best_model       = "eval_exact_match",
        greater_is_better           = True,
        fp16                        = dev["codegen_fp16"],
        bf16                        = dev["codegen_bf16"],
        report_to                   = "none",
        dataloader_drop_last        = False
    )

    trainer = Trainer(
        model                         = model,
        args                          = training_args,
        train_dataset                 = train_split,
        eval_dataset                  = eval_split,
        data_collator                 = data_collator,
        compute_metrics               = compute_metrics               if use_eval else None,
        preprocess_logits_for_metrics = preprocess_logits_for_metrics if use_eval else None,
    )

    pipeline_logger.info("fine_tuning", "training_start", stats={
        "samples": len(train_split),
        "eval_samples": len(eval_split) if eval_split else 0,
        "epochs": cfg["epochs"],
        "steps_per_epoch": max(1, -(-len(train_split) // (cfg["train_batch"] * cfg["grad_accum"]))),
        "logging_steps": 200,
        "save_strategy": "epoch",
        "load_best_model_at_end": use_eval,
        "fp16": dev["codegen_fp16"],
        "bf16": dev["codegen_bf16"]
    })
    print(f"[Execution Engine] Launching Optimization sequence...")
    resume_ckpt = True if args.resume_training else None
    trainer.train(resume_from_checkpoint=resume_ckpt)

    trainer.save_model(checkpoint_path)
    tokenizer.save_pretrained(checkpoint_path)

    pipeline_logger.info("fine_tuning", "training_complete", stats={
        "checkpoint_path": checkpoint_path
    })
    print(f"[Execution Engine] Training Complete. Output stored at {checkpoint_path}")


if __name__ == "__main__":
    main()
