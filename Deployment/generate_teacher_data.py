"""Teacher annotation + execution-based verification filter (plan §6, SPEC §10 step 12).

For each mined failure the teacher writes a short ``teacher_analysis`` (≤15 words)
explaining the delta between the ``broken_draft`` and the gold — a diff-explanation
task, since the teacher is *given* the gold. It also returns a ``corrected_query``
used **only** as a verification check:

    keep the analysis  ⇔  corrected_query is EXECUTION-correct against gold.

Correctness here is decided by execution (``sql_exec`` / ``mongo_exec``), never by
string match — matching by string would re-introduce the exact bug this project
exists to fix (plan §2 change #2, SPEC-REVIEW #6). The verified failures define the
Stage-B sample set shared by BOTH Pass-2 arms (control swaps in a neutral analysis,
teacher uses this one), so the arms differ only in the analysis slot (plan §8).

Backends: ``--mock`` (deterministic, for dev/sanity — returns gold as the corrected
query so the pipeline runs without the 14B), ``local`` (Qwen2.5-Coder-14B on MPS,
loaded then freed), ``api`` (OpenAI-compatible). The ``max_failures`` cap samples
reproducibly (``failure_sample_seed``) and the dropped count is logged (no silent
truncation, plan §8). The discard rate from the filter is logged too.

Run:
    python generate_teacher_data.py --mock            # dev / sanity
    python generate_teacher_data.py --provider local  # real Qwen teacher
    python generate_teacher_data.py --provider api --base_url ... --model_id ...
"""

from __future__ import annotations

import argparse
import json
import logging
import random

from src import config, loader, mongo_exec, sql_exec
from src.logger import setup_logging

log = logging.getLogger(__name__)


# --- Teacher prompt --------------------------------------------------------
def _schema_for(task: str, db_id: str) -> str:
    if task == "text2sql":
        return loader.load_sql_schema_map().get(db_id, "")
    return loader.load_nosql_schema_map().get(db_id, "")


def build_teacher_prompt(rec: dict) -> str:
    """Diff-explanation prompt: given the wrong draft AND the gold, explain the delta."""
    task = rec["task"]
    input_str = rec["source_sql"] if task == "sql2nosql" else rec["question"]
    kind = "SQL" if task == "text2sql" else "MongoDB (MQL)"
    return (
        f"You are a database query expert. A student translated a task into {kind} incorrectly.\n"
        f"Schema: {_schema_for(task, rec['db_id'])}\n"
        f"Input: {input_str}\n"
        f"Student's wrong answer: {rec['broken_draft']}\n"
        f"Correct answer: {rec['gold']}\n\n"
        f"In at most {config.CONFIG.teacher.analysis_max_words} words, explain what the student "
        f"got wrong. Then repeat the corrected query. Respond EXACTLY as:\n"
        f"Analysis: <short explanation>\n"
        f"Corrected: <the corrected query>"
    )


def parse_teacher_output(text: str, gold: str) -> tuple[str, str]:
    """Extract (analysis, corrected_query) from the teacher's raw text; tolerant."""
    analysis, corrected = "", ""
    for line in text.splitlines():
        s = line.strip()
        if s.lower().startswith("analysis:"):
            analysis = s.split(":", 1)[1].strip()
        elif s.lower().startswith("corrected:"):
            corrected = s.split(":", 1)[1].strip()
    # Cap analysis length defensively.
    words = analysis.split()
    if len(words) > config.CONFIG.teacher.analysis_max_words:
        analysis = " ".join(words[: config.CONFIG.teacher.analysis_max_words])
    return analysis, corrected


# --- Backends --------------------------------------------------------------
class MockTeacher:
    """Deterministic teacher for dev/sanity: canned analysis + gold as corrected."""

    def annotate(self, records: list[dict]) -> list[str]:
        outs = []
        for r in records:
            outs.append(f"Analysis: draft diverged from the gold on filter/shape.\nCorrected: {r['gold']}")
        return outs


class LocalTeacher:
    """Qwen2.5-Coder-14B in-process on MPS/bf16, loaded then freed (plan §6)."""

    def __init__(self):
        self.model = None
        self.tok = None

    def _load(self):
        from transformers import AutoModelForCausalLM, AutoTokenizer
        from src.device import get_device, get_dtype
        tc = config.CONFIG.teacher
        log.info("loading teacher %s on MPS bf16 (~30GB) — do not run concurrently with training", tc.model_id)
        self.tok = AutoTokenizer.from_pretrained(tc.model_id)
        self.model = AutoModelForCausalLM.from_pretrained(tc.model_id, dtype=get_dtype())
        self.model.to(get_device())
        self.model.eval()

    def annotate(self, records: list[dict]) -> list[str]:
        import torch
        from src.device import get_device
        if self.model is None:
            self._load()
        tc = config.CONFIG.teacher
        outs = []
        for r in records:
            messages = [{"role": "user", "content": build_teacher_prompt(r)}]
            text = self.tok.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
            enc = self.tok(text, return_tensors="pt").to(get_device())
            with torch.no_grad():
                gen = self.model.generate(**enc, max_new_tokens=tc.max_output_tokens,
                                          temperature=tc.temperature, do_sample=tc.temperature > 0,
                                          pad_token_id=self.tok.eos_token_id)
            outs.append(self.tok.decode(gen[0, enc["input_ids"].shape[1]:], skip_special_tokens=True))
        return outs

    def free(self):
        from src.model_factory import free_model
        if self.model is not None:
            free_model(self.model)
            self.model = None


class ApiTeacher:
    """OpenAI-compatible chat-completions backend (hosted Qwen fallback, plan §6)."""

    def __init__(self, base_url: str, model_id: str, api_key: str | None = None):
        self.base_url = base_url.rstrip("/")
        self.model_id = model_id
        self.api_key = api_key or "EMPTY"

    def annotate(self, records: list[dict]) -> list[str]:
        import requests
        tc = config.CONFIG.teacher
        outs = []
        for r in records:
            resp = requests.post(
                f"{self.base_url}/chat/completions",
                headers={"Authorization": f"Bearer {self.api_key}"},
                json={
                    "model": self.model_id,
                    "messages": [{"role": "user", "content": build_teacher_prompt(r)}],
                    "temperature": tc.temperature,
                    "max_tokens": tc.max_output_tokens,
                },
                timeout=60,
            )
            resp.raise_for_status()
            outs.append(resp.json()["choices"][0]["message"]["content"])
        return outs


def make_teacher(args):
    if args.mock or args.provider == "mock":
        return MockTeacher()
    if args.provider == "local":
        return LocalTeacher()
    if args.provider == "api":
        if not args.base_url:
            raise SystemExit("--provider api requires --base_url")
        return ApiTeacher(args.base_url, args.model_id or config.CONFIG.teacher.model_id, args.api_key)
    raise SystemExit(f"unknown provider {args.provider!r}")


# --- Verification filter (execution-based) ---------------------------------
def corrected_is_correct(rec: dict, corrected: str) -> bool:
    task, db_id, gold = rec["task"], rec["db_id"], rec["gold"]
    if not corrected:
        return False
    if task == "text2sql":
        return sql_exec.is_correct(db_id, gold, corrected)
    order_sensitive = mongo_exec.implies_order(gold_sql=rec.get("aux_sql"), gold_mql=gold)
    return mongo_exec.is_correct(db_id, gold, corrected, order_sensitive)


# --- Failure loading + sampling --------------------------------------------
def load_failures() -> list[dict]:
    all_failures = []
    for task in config.TASKS:
        p = config.FAILURES_DIR / f"{task}_failures.json"
        if p.exists():
            all_failures += json.loads(p.read_text(encoding="utf-8"))
    return all_failures


def sample_failures(failures: list[dict], max_failures: int, seed: int) -> list[dict]:
    """Cap at max_failures, sampling reproducibly; log how many were dropped."""
    if len(failures) <= max_failures:
        return failures
    rng = random.Random(seed)
    idx = list(range(len(failures)))
    rng.shuffle(idx)
    kept = [failures[i] for i in sorted(idx[:max_failures])]
    dropped = len(failures) - len(kept)
    log.warning("max_failures cap: kept %d, DROPPED %d failures (seed=%d) — not silent",
                len(kept), dropped, seed)
    return kept


# --- Main ------------------------------------------------------------------
def run(args) -> dict:
    tc = config.CONFIG.teacher
    failures = load_failures()
    if not failures:
        raise SystemExit("no failures on disk — run extract_failures.py first")
    if args.limit is not None:
        failures = failures[: args.limit]

    sampled = sample_failures(failures, tc.max_failures, tc.failure_sample_seed)
    log.info("annotating %d failures with teacher (%s)", len(sampled),
             "mock" if (args.mock or args.provider == "mock") else args.provider)

    teacher = make_teacher(args)
    raw_outputs = teacher.annotate(sampled)
    if hasattr(teacher, "free"):
        teacher.free()  # free the 14B before anything else touches memory

    config.ensure_dirs()
    kept_by_task: dict[str, list] = {t: [] for t in config.TASKS}
    n_kept = n_discarded = 0
    for rec, raw in zip(sampled, raw_outputs):
        analysis, corrected = parse_teacher_output(raw, rec["gold"])
        if config.CONFIG.teacher.verify_against_gold and not corrected_is_correct(rec, corrected):
            n_discarded += 1
            continue
        n_kept += 1
        kept_by_task[rec["task"]].append({
            "db_id": rec["db_id"], "task": rec["task"],
            "question": rec.get("question"), "source_sql": rec.get("source_sql"),
            "aux_sql": rec.get("aux_sql"), "gold": rec["gold"],
            "broken_draft": rec["broken_draft"], "teacher_analysis": analysis,
        })

    for task, rows in kept_by_task.items():
        (config.AUGMENTED_DIR / f"{task}_augmented.json").write_text(
            json.dumps(rows, indent=1), encoding="utf-8")

    discard_rate = round(n_discarded / max(len(sampled), 1), 4)
    summary = {
        "failures_total": len(failures), "sampled": len(sampled),
        "dropped_by_cap": len(failures) - len(sampled),
        "kept": n_kept, "discarded_by_filter": n_discarded, "discard_rate": discard_rate,
        "per_task_kept": {t: len(v) for t, v in kept_by_task.items()},
    }
    log.info("teacher done: %s", summary)
    return summary


def main() -> None:
    ap = argparse.ArgumentParser(description="Teacher annotation + execution verification filter.")
    ap.add_argument("--provider", choices=("mock", "local", "api"), default="local")
    ap.add_argument("--mock", action="store_true", help="deterministic mock teacher (dev/sanity)")
    ap.add_argument("--base_url", help="OpenAI-compatible base URL (provider api)")
    ap.add_argument("--model_id", help="override teacher model id")
    ap.add_argument("--api_key", help="API key (provider api)")
    ap.add_argument("--limit", type=int, default=None)
    ap.add_argument("--sanity", action="store_true")
    args = ap.parse_args()

    setup_logging("generate_teacher_data")
    if args.sanity:
        args.mock = True
        if args.limit is None:
            args.limit = 12
    summary = run(args)
    print(summary)


if __name__ == "__main__":
    main()
