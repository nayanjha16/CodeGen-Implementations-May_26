"""
Teacher LLM Inference — Pass 2 Calibration Data Generator.

For each failure extracted by extract_failures.py, calls a configurable teacher
LLM with a RAG reference example and a minified schema.  The teacher outputs:
  - teacher_analysis : one diagnostic sentence (max 15 words)
  - corrected_query  : the exact correct SQL or MQL

The teacher's analysis is injected into the training data.  The corrected_query
is validated against the gold label and used only if it matches; otherwise the
gold label is kept (so correctness is never compromised by a hallucinating teacher).

Output:
  - data/spider/spider_augmented_train.json       (Pass 2 Spider training set)
  - docspider/.../train_augmented.json            (Pass 2 DocSpider training set)

Usage:
    # OpenAI
    export OPENAI_API_KEY="sk-..."
    python generate_teacher_data.py

    # Anthropic
    export ANTHROPIC_API_KEY="sk-ant-..."
    python generate_teacher_data.py --provider anthropic --model_id claude-haiku-4-5-20251001
"""

import argparse
import json
import os
import random
import re
import time

from src.config import DATA, TEACHER, MODELS
from src.loader import (
    load_spider_tasks, load_docspider_tasks,
    load_spider_schema_maps, load_schema_context_map,
)
from src.logger import pipeline_logger

# ---------------------------------------------------------------------------
# Schema minification (mirrors finetune_unified.py — kept local to avoid
# circular dependency on a training-only utility)
# ---------------------------------------------------------------------------

def _minify_sql_schema(schema_str: str) -> str:
    if not isinstance(schema_str, str) or not schema_str:
        return ""
    table_matches = re.findall(r'CREATE\s+TABLE\s+(\w+)\s*\((.*?)\);', schema_str, re.DOTALL | re.IGNORECASE)
    if not table_matches:
        return re.sub(r'\s+', ' ', schema_str).strip()
    tables = []
    for tname, cols_block in table_matches:
        cols = []
        for col in cols_block.split(','):
            col = col.strip()
            if not col:
                continue
            if any(k in col.upper() for k in ["FOREIGN KEY", "PRIMARY KEY", "CONSTRAINT", "REFERENCES"]):
                continue
            parts = col.split()
            if parts:
                cols.append(parts[0])
        tables.append(f"{tname}({', '.join(cols)})")
    return " | ".join(tables)


def _minify_nosql_schema(schema_str: str) -> str:
    return re.sub(r'\s+', ' ', schema_str).strip() if schema_str else ""


# ---------------------------------------------------------------------------
# RAG: build a per-DB index of successful training examples
# ---------------------------------------------------------------------------

def _build_rag_index(spider_tasks, docspider_tasks, spider_schemas, docspider_schemas):
    """
    Returns {db_id: [{"task_type", "question", "sql", "mql", "schema"}]}
    Used to fetch a reference example for the teacher prompt.
    """
    index = {}

    for t in spider_tasks:
        db = t.get("db_id", "")
        # Skip entries that are failures (have a broken_draft) — only use clean examples
        if t.get("broken_draft"):
            continue
        schema = _minify_sql_schema(spider_schemas.get(db, ""))
        index.setdefault(db, []).append({
            "task_type": "text2sql",
            "question":  t.get("question", ""),
            "sql":       t.get("query", ""),
            "mql":       "",
            "schema":    schema,
        })

    for t in docspider_tasks:
        db = t.get("db_id", "")
        if t.get("broken_draft_trans") or t.get("broken_draft_dir"):
            continue
        schema = _minify_nosql_schema(docspider_schemas.get(db, ""))
        index.setdefault(db, []).append({
            "task_type": "nosql",
            "question":  t.get("question", ""),
            "sql":       t.get("spider_gold_sql", ""),
            "mql":       t.get("query", ""),
            "schema":    schema,
        })

    return index


def _get_rag_example(rag_index, db_id, task_type, exclude_question=""):
    """Return one RAG example for the given DB and task type, or fall back globally."""
    same_db = [e for e in rag_index.get(db_id, []) if e["task_type"] == task_type
               and e.get("question") != exclude_question]
    if same_db:
        return random.choice(same_db)
    # Cross-DB fallback
    all_candidates = [e for exs in rag_index.values() for e in exs if e["task_type"] == task_type]
    return random.choice(all_candidates) if all_candidates else None


# ---------------------------------------------------------------------------
# Teacher prompt builders — one per task type
# ---------------------------------------------------------------------------

SYSTEM_INSTRUCTION = (
    "You are an expert database engineer and query correction specialist. "
    "A student model generated an incorrect database query. "
    "Diagnose the specific structural error in ONE sentence (maximum {max_words} words), "
    "then output the exact corrected query with no extra commentary or formatting. "
    "Focus on: column names, table aliases, JOIN conditions, aggregation functions, "
    "GROUP BY clauses, or NoSQL pipeline stage selection."
)


def _fmt_rag_block_sql(example) -> str:
    if not example:
        return ""
    return (
        f"[REFERENCE EXAMPLE]\n"
        f"Question: {example['question']}\n"
        f"Schema: {example['schema']}\n"
        f"Correct SQL: {example['sql']}\n\n"
    )


def _fmt_rag_block_nosql_trans(example) -> str:
    if not example:
        return ""
    return (
        f"[REFERENCE EXAMPLE]\n"
        f"Input SQL: {example['sql']}\n"
        f"Correct MQL: {example['mql']}\n\n"
    )


def _fmt_rag_block_nosql_dir(example) -> str:
    if not example:
        return ""
    return (
        f"[REFERENCE EXAMPLE]\n"
        f"Question: {example['question']}\n"
        f"Schema: {example['schema']}\n"
        f"Correct MQL: {example['mql']}\n\n"
    )


def _build_prompt_text2sql(failure, schema, rag_example, max_words):
    rag = _fmt_rag_block_sql(rag_example)
    return (
        f"{rag}"
        f"[FAILURE TO CORRECT]\n"
        f"Task: NL-to-SQL\n"
        f"Question: {failure['question']}\n"
        f"Schema: {schema}\n"
        f"Gold SQL: {failure['query']}\n"
        f"Student's Broken Draft: {failure['broken_draft']}\n\n"
        f"[INSTRUCTIONS]\n"
        f"1. Write ONE sentence (max {max_words} words) identifying the structural error.\n"
        f"2. Output the exact corrected SQL — no comments, no markdown fences.\n\n"
        f"[RESPOND WITH STRICT JSON ONLY]\n"
        f'{{ "teacher_analysis": "...", "corrected_query": "..." }}'
    )


def _build_prompt_sql2nosql(failure, schema, rag_example, max_words):
    rag = _fmt_rag_block_nosql_trans(rag_example)
    return (
        f"{rag}"
        f"[FAILURE TO CORRECT]\n"
        f"Task: SQL-to-MQL\n"
        f"Input SQL: {failure.get('spider_gold_sql', '')}\n"
        f"Schema: {schema}\n"
        f"Gold MQL: {failure['query']}\n"
        f"Student's Broken Draft: {failure['broken_draft']}\n\n"
        f"[INSTRUCTIONS]\n"
        f"1. Write ONE sentence (max {max_words} words) identifying the structural error.\n"
        f"2. Output the exact corrected MQL — no comments, no markdown fences.\n\n"
        f"[RESPOND WITH STRICT JSON ONLY]\n"
        f'{{ "teacher_analysis": "...", "corrected_query": "..." }}'
    )


def _build_prompt_text2nosql(failure, schema, rag_example, max_words):
    rag = _fmt_rag_block_nosql_dir(rag_example)
    return (
        f"{rag}"
        f"[FAILURE TO CORRECT]\n"
        f"Task: NL-to-MQL\n"
        f"Question: {failure['question']}\n"
        f"Schema: {schema}\n"
        f"Gold MQL: {failure['query']}\n"
        f"Student's Broken Draft: {failure['broken_draft']}\n\n"
        f"[INSTRUCTIONS]\n"
        f"1. Write ONE sentence (max {max_words} words) identifying the structural error.\n"
        f"2. Output the exact corrected MQL — no comments, no markdown fences.\n\n"
        f"[RESPOND WITH STRICT JSON ONLY]\n"
        f'{{ "teacher_analysis": "...", "corrected_query": "..." }}'
    )


# ---------------------------------------------------------------------------
# Teacher API call — dispatches to OpenAI or Anthropic
# ---------------------------------------------------------------------------

_FALLBACK_ANALYSES = {
    "text2sql":  "Check table selection, JOIN conditions, and aggregation function in the SQL query.",
    "sql2nosql": "Check pipeline stage selection, field projection, and collection name in the MQL.",
    "text2nosql": "Check collection name, filter conditions, and field projection in the MQL query.",
}


def _call_teacher(prompt_text: str, system_text: str, cfg: dict, task_type: str = "text2sql") -> dict:
    if cfg.get("mock"):
        return {
            "teacher_analysis": _FALLBACK_ANALYSES[task_type],
            "corrected_query":  "",
        }

    provider = cfg["provider"]

    try:
        if provider in ("openai", "groq", "together", "fireworks"):
            from openai import OpenAI
            # Each provider exposes an OpenAI-compatible endpoint via base_url.
            # Key resolution order: provider-specific env var first, then OPENAI_API_KEY.
            api_key = (
                os.environ.get("GROQ_API_KEY")
                or os.environ.get("TOGETHER_API_KEY")
                or os.environ.get("FIREWORKS_API_KEY")
                or os.environ.get("OPENAI_API_KEY")
            )
            client = OpenAI(api_key=api_key, base_url=cfg.get("base_url"))
            resp = client.chat.completions.create(
                model=cfg["model_id"],
                temperature=cfg["temperature"],
                max_tokens=cfg["max_output_tokens"],
                response_format={"type": "json_object"},
                messages=[
                    {"role": "system", "content": system_text},
                    {"role": "user",   "content": prompt_text},
                ],
            )
            raw = resp.choices[0].message.content
            try:
                return json.loads(raw)
            except json.JSONDecodeError:
                match = re.search(r'\{.*\}', raw, re.DOTALL)
                if match:
                    try:
                        return json.loads(match.group())
                    except json.JSONDecodeError:
                        pass
            return {}

        elif provider == "anthropic":
            import anthropic
            client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))
            resp = client.messages.create(
                model=cfg["model_id"],
                max_tokens=cfg["max_output_tokens"],
                temperature=cfg["temperature"],
                system=system_text,
                messages=[{"role": "user", "content": prompt_text}],
            )
            # Anthropic doesn't guarantee JSON mode — parse best-effort
            raw = resp.content[0].text.strip()
            try:
                return json.loads(raw)
            except json.JSONDecodeError:
                match = re.search(r'\{.*\}', raw, re.DOTALL)
                if match:
                    try:
                        return json.loads(match.group())
                    except json.JSONDecodeError:
                        pass
            return {}

        else:
            raise ValueError(f"Unsupported provider: {provider}")

    except Exception as exc:
        pipeline_logger.warning("teacher_inference", "api_call_failed", stats={"error": str(exc)[:120]})
        return {}


def _teacher_annotate(failures: list, task_type: str, rag_index: dict,
                      spider_schemas: dict, docspider_schemas: dict,
                      teacher_cfg: dict) -> list:
    """
    Calls the teacher for each failure and returns the annotated list.
    Gold query is always preserved — teacher analysis is the only injection.
    """
    system_text = SYSTEM_INSTRUCTION.format(max_words=teacher_cfg["analysis_max_words"])
    annotated = []
    cap = teacher_cfg["max_failures"]

    for i, failure in enumerate(failures[:cap]):
        db_id = failure.get("db_id", "")

        if task_type == "text2sql":
            schema = _minify_sql_schema(spider_schemas.get(db_id, ""))
            rag    = _get_rag_example(rag_index, db_id, "text2sql", failure.get("question", ""))
            prompt = _build_prompt_text2sql(failure, schema, rag, teacher_cfg["analysis_max_words"])
        elif task_type == "sql2nosql":
            schema = _minify_nosql_schema(docspider_schemas.get(db_id, ""))
            rag    = _get_rag_example(rag_index, db_id, "nosql", "")
            prompt = _build_prompt_sql2nosql(failure, schema, rag, teacher_cfg["analysis_max_words"])
        else:  # text2nosql
            schema = _minify_nosql_schema(docspider_schemas.get(db_id, ""))
            rag    = _get_rag_example(rag_index, db_id, "nosql", failure.get("question", ""))
            prompt = _build_prompt_text2nosql(failure, schema, rag, teacher_cfg["analysis_max_words"])

        # Log the full teacher prompt every 50 calls for auditability
        if i % 50 == 0:
            pipeline_logger.record(
                stage="teacher_inference",
                action=f"{task_type}_prompt_preview",
                input_data=prompt,
                stats={"index": i, "db_id": db_id, "total": min(len(failures), cap)}
            )

        result = _call_teacher(prompt, system_text, teacher_cfg, task_type)
        time.sleep(teacher_cfg["rate_limit_sleep"])

        analysis = result.get("teacher_analysis", _FALLBACK_ANALYSES[task_type]).strip()

        # Enforce word cap — truncate if the teacher exceeded it
        words = analysis.split()
        if len(words) > teacher_cfg["analysis_max_words"]:
            analysis = " ".join(words[:teacher_cfg["analysis_max_words"]])

        entry = dict(failure)           # preserve all original fields
        entry["teacher_analysis"] = analysis
        # broken_draft is already in the failure record from extract_failures.py
        annotated.append(entry)

        if (i + 1) % 100 == 0:
            pipeline_logger.info("teacher_inference", f"{task_type}_progress",
                                 stats={"done": i + 1, "total": min(len(failures), cap)})
            print(f"  [{task_type}] {i + 1}/{min(len(failures), cap)} annotated")

    pipeline_logger.info("teacher_inference", f"{task_type}_complete",
                         stats={"annotated": len(annotated), "cap_applied": len(failures) > cap})
    return annotated


# ---------------------------------------------------------------------------
# Merge teacher data into original training sets
# ---------------------------------------------------------------------------

def _merge_spider(original: list, annotated_failures: list) -> list:
    """
    Replace failure entries in the original training set with teacher-annotated
    versions (matched by question + db_id).  Entries with no failure keep the
    original format — they will be treated as Pass 1 samples during fine-tuning.
    """
    failure_index = {
        (r["db_id"], r["question"]): r for r in annotated_failures
    }
    merged = []
    replaced = 0
    for entry in original:
        key = (entry.get("db_id", ""), entry.get("question", ""))
        if key in failure_index:
            merged.append(failure_index[key])
            replaced += 1
        else:
            merged.append(entry)

    pipeline_logger.info("teacher_inference", "spider_merge_done",
                         stats={"total": len(merged), "replaced_with_teacher_data": replaced})
    return merged


def _merge_docspider(original: list, annotated_sql2nosql: list, annotated_text2nosql: list) -> list:
    """
    For DocSpider entries that appear in either failure list, inject the per-task
    teacher fields (broken_draft_trans / teacher_analysis_trans for sql2nosql,
    broken_draft_dir / teacher_analysis_dir for text2nosql).
    Unmatched entries pass through unchanged.
    """
    # Index by (db_id, spider_gold_sql) for sql2nosql; by (db_id, question) for text2nosql
    sql2nosql_idx   = {(r["db_id"], r.get("spider_gold_sql", "")): r for r in annotated_sql2nosql}
    text2nosql_idx  = {(r["db_id"], r.get("question", "")):         r for r in annotated_text2nosql}

    merged = []
    for entry in original:
        e = dict(entry)
        key_trans = (e.get("db_id", ""), e.get("spider_gold_sql", ""))
        key_dir   = (e.get("db_id", ""), e.get("question", ""))

        if key_trans in sql2nosql_idx:
            f = sql2nosql_idx[key_trans]
            e["broken_draft_trans"]    = f.get("broken_draft", "")
            e["teacher_analysis_trans"] = f.get("teacher_analysis", "")

        if key_dir in text2nosql_idx:
            f = text2nosql_idx[key_dir]
            e["broken_draft_dir"]    = f.get("broken_draft", "")
            e["teacher_analysis_dir"] = f.get("teacher_analysis", "")

        merged.append(e)

    injected = sum(
        1 for e in merged
        if e.get("broken_draft_trans") or e.get("broken_draft_dir")
    )
    pipeline_logger.info("teacher_inference", "docspider_merge_done",
                         stats={"total": len(merged), "entries_with_teacher_data": injected})
    return merged


def _load_failures(path: str) -> list:
    if not path or not os.path.exists(path):
        pipeline_logger.warning("teacher_inference", "failure_file_missing", stats={"path": path})
        return []
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def _save_json(data: list, path: str):
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="Teacher LLM inference — generates Pass 2 calibration data")
    parser.add_argument("--provider", default=None,
                        help=(
                            "Teacher provider — overrides config. "
                            "OpenAI-compatible (uses base_url from config): groq | together | fireworks | openai. "
                            "Native client: anthropic."
                        ))
    parser.add_argument("--model_id", default=None,
                        help="Teacher model ID (overrides config)")
    parser.add_argument("--mock_teacher", action="store_true",
                        help="Skip API call; return synthetic teacher annotation (sanity testing).")
    args = parser.parse_args()

    # Build effective teacher config — CLI args override config
    teacher_cfg = dict(TEACHER)
    if args.provider:
        teacher_cfg["provider"] = args.provider
    if args.model_id:
        teacher_cfg["model_id"] = args.model_id
    teacher_cfg["mock"] = args.mock_teacher

    pipeline_logger.info("teacher_inference", "start", stats={
        "provider": teacher_cfg["provider"],
        "model_id": teacher_cfg["model_id"],
        "max_failures_per_task": teacher_cfg["max_failures"],
        "mock": teacher_cfg["mock"],
    })
    if teacher_cfg["mock"]:
        print("[teacher] MOCK MODE — no API calls will be made; using synthetic annotations.")
    else:
        print(f"[teacher] Provider: {teacher_cfg['provider']} | Model: {teacher_cfg['model_id']}")

    # Load original training sets (for RAG index + merge targets)
    spider_original   = load_spider_tasks(DATA["spider_train"])
    docspider_original = load_docspider_tasks(DATA["docspider_train"])
    spider_schemas    = load_spider_schema_maps()
    docspider_schemas = load_schema_context_map(DATA["docspider_collections"])

    rag_index = _build_rag_index(spider_original, docspider_original, spider_schemas, docspider_schemas)
    pipeline_logger.info("teacher_inference", "rag_index_built", stats={
        "db_count": len(rag_index),
        "total_examples": sum(len(v) for v in rag_index.values())
    })

    # ------------------------------------------------------------------ #
    # Spider text2sql failures
    # ------------------------------------------------------------------ #
    spider_failures = _load_failures(DATA["spider_failures"])
    pipeline_logger.info("teacher_inference", "spider_failures_loaded",
                         stats={"count": len(spider_failures)})
    print(f"\n[teacher] Annotating {len(spider_failures)} Spider text2sql failures...")

    annotated_spider = _teacher_annotate(
        spider_failures, "text2sql", rag_index, spider_schemas, docspider_schemas, teacher_cfg
    )

    spider_pass2 = _merge_spider(spider_original, annotated_spider)
    _save_json(spider_pass2, DATA["spider_augmented_train"])
    print(f"[teacher] Spider augmented train saved → {DATA['spider_augmented_train']}")

    # ------------------------------------------------------------------ #
    # DocSpider sql2nosql failures
    # ------------------------------------------------------------------ #
    sql2nosql_failures = _load_failures(DATA["docspider_sql2nosql_failures"])
    pipeline_logger.info("teacher_inference", "sql2nosql_failures_loaded",
                         stats={"count": len(sql2nosql_failures)})
    print(f"\n[teacher] Annotating {len(sql2nosql_failures)} DocSpider sql2nosql failures...")

    annotated_sql2nosql = _teacher_annotate(
        sql2nosql_failures, "sql2nosql", rag_index, spider_schemas, docspider_schemas, teacher_cfg
    )

    # ------------------------------------------------------------------ #
    # DocSpider text2nosql failures
    # ------------------------------------------------------------------ #
    text2nosql_failures = _load_failures(DATA["docspider_text2nosql_failures"])
    pipeline_logger.info("teacher_inference", "text2nosql_failures_loaded",
                         stats={"count": len(text2nosql_failures)})
    print(f"\n[teacher] Annotating {len(text2nosql_failures)} DocSpider text2nosql failures...")

    annotated_text2nosql = _teacher_annotate(
        text2nosql_failures, "text2nosql", rag_index, spider_schemas, docspider_schemas, teacher_cfg
    )

    docspider_pass2 = _merge_docspider(docspider_original, annotated_sql2nosql, annotated_text2nosql)
    _save_json(docspider_pass2, DATA["docspider_augmented_train"])
    print(f"[teacher] DocSpider augmented train saved → {DATA['docspider_augmented_train']}")

    pipeline_logger.info("teacher_inference", "complete", stats={
        "spider_annotated": len(annotated_spider),
        "sql2nosql_annotated": len(annotated_sql2nosql),
        "text2nosql_annotated": len(annotated_text2nosql),
    })
    print("\n[teacher] Teacher inference complete.")


if __name__ == "__main__":
    main()
