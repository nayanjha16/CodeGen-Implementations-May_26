"""Single source of truth for paths, hyperparameters, and endpoints.

Scripts import from here; nothing hardcodes a path or a knob. See SPEC.md §5.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path

# --- Reproducibility -------------------------------------------------------
SEED = 42  # plan.md §3 — required, logged everywhere.

# --- Paths -----------------------------------------------------------------
PROJECT_ROOT = Path(__file__).resolve().parents[1]

SPIDER_DIR = PROJECT_ROOT / "data" / "spider"
DOCSPIDER_DIR = PROJECT_ROOT / "docspider" / "docspider_ground_truth_dataset"
SPIDER_DB_DIR = SPIDER_DIR / "database"  # SQLite DBs, also the Mongo load source

MODELS_DIR = PROJECT_ROOT / "models"
OUTPUTS_DIR = PROJECT_ROOT / "outputs"
RETRIEVAL_INDEX_DIR = PROJECT_ROOT / "retrieval_index"
LOGS_DIR = PROJECT_ROOT / "logs"
SPLITS_DIR = OUTPUTS_DIR / "splits"  # persisted train/valid partition (reproducible)
# Generated pipeline artifacts kept under outputs/ (never written into the vendored
# docspider/ git repo or the source data dirs). See DECISIONS.md (step 11).
FAILURES_DIR = OUTPUTS_DIR / "codegen" / "failures"      # extract_failures.py output
AUGMENTED_DIR = OUTPUTS_DIR / "codegen" / "augmented"    # generate_teacher_data.py output

# Checkpoint locations for the three experiment arms (plan.md §8).
PASS1_DIR = MODELS_DIR / "codegen_pass1"
PASS2_CONTROL_DIR = MODELS_DIR / "codegen_pass2_control"
PASS2_TEACHER_DIR = MODELS_DIR / "codegen_pass2_teacher"


# --- Model -----------------------------------------------------------------
@dataclass(frozen=True)
class ModelConfig:
    # Open decision (SPEC §9): switched to Qwen2.5-Coder-1.5B (2026-07-18, user) for a
    # stronger student — plan §3 warns CodeGen-350M may be too weak for the distillation
    # signal to appear. target_modules are Qwen2's attention/MLP projection names and
    # MUST match the base model (they changed from CodeGen's qkv_proj/out_proj/fc_*).
    base_model: str = "Qwen/Qwen2.5-Coder-1.5B"
    # Trimmed 2048→768 (2026-07-18) to fit MPS memory — full 2048 drove the machine
    # into heavy swap (step time degraded 3s→90s). Prompts here (schema+question+draft)
    # fit comfortably in 768; see DECISIONS.md.
    max_len: int = 768
    lora_r: int = 16
    lora_alpha: int = 32
    lora_dropout: float = 0.05
    lora_target_modules: tuple[str, ...] = (
        "q_proj", "k_proj", "v_proj", "o_proj",  # attention
        "gate_proj", "up_proj", "down_proj",      # MLP
    )


# --- Data splits -----------------------------------------------------------
@dataclass(frozen=True)
class SplitConfig:
    valid_fraction: float = 0.10  # carved from train; dev is never touched (plan.md §4)


# --- Training --------------------------------------------------------------
@dataclass(frozen=True)
class TrainConfig:
    epochs_max: int = 2  # trimmed 5→2 (2026-07-18) for MPS feasibility; early stopping still on
    batch_size: int = 4
    grad_accum: int = 4  # effective batch = 16
    lr_pass1: float = 2e-4
    lr_pass2: float = 5e-5  # continues from Pass 1 weights; reuse of 2e-4 would wreck them
    warmup_ratio: float = 0.03
    weight_decay: float = 0.01
    early_stopping: bool = True
    load_best_model_at_end: bool = True
    mask_prompt_tokens: bool = True  # loss on completion tokens only (plan.md §3)
    save_steps: int = 200  # frequent checkpoints; resume-friendly
    # Multi-task balance (SPEC §9 #3, decided 2026-07-18): "loss_weight" scales each
    # task's loss so the three contribute equal gradient influence with every example
    # seen once. "upsample" is superseded — duplicating ~73% of Mongo data drove
    # memorisation that starved NoSQL failure mining (SPEC-REVIEW #4).
    task_balance: str = "loss_weight"


# --- Inference -------------------------------------------------------------
@dataclass(frozen=True)
class InferConfig:
    max_new_tokens: int = 150
    num_beams: int = 2
    two_stage: bool = True  # draft -> revise (plan.md §9)


# --- RAG -------------------------------------------------------------------
@dataclass(frozen=True)
class RagConfig:
    train_with_retrieval: bool = True  # train on retrieved, not random, examples (plan.md §7)
    no_reference_fraction: float = 0.20  # keep the no-RAG inference path in-distribution
    embedding_model: str = "BAAI/bge-small-en-v1.5"


# --- MongoDB execution harness ---------------------------------------------
@dataclass(frozen=True)
class MongoConfig:
    # Defaults are localhost (unchanged on the Mac); overridable via env so a
    # multi-container deploy can point the executor at a separate Mongo service
    # (e.g. MONGO_HOST=mongo). Read once at import — still the single source of truth.
    host: str = os.environ.get("MONGO_HOST", "127.0.0.1")
    port: int = int(os.environ.get("MONGO_PORT", "27017"))
    # Per-query timeout — for pipeline liveness (a pathological aggregation must
    # not stall a 3,000-query mining run), NOT data safety. No auth / RO user /
    # denylist by design; see SPEC §4.4 for the risk-acceptance rationale.
    eval_timeout_s: float = 10.0

    @property
    def uri(self) -> str:
        return f"mongodb://{self.host}:{self.port}"


# --- Teacher ---------------------------------------------------------------
@dataclass(frozen=True)
class TeacherConfig:
    backend: str = "local"  # "local" (transformers on MPS) | "api" (OpenAI-compatible)
    model_id: str = "Qwen/Qwen2.5-Coder-14B-Instruct"  # ~30GB bf16, loaded then freed
    api_base_url: str | None = None  # only for backend == "api"
    temperature: float = 0.2
    max_output_tokens: int = 300
    analysis_max_words: int = 15
    max_failures: int = 3000
    failure_sample_seed: int = 42  # document which 3000 were annotated
    verify_against_gold: bool = True  # discard analyses whose corrected_query != gold (plan.md §6)


# --- Aggregate -------------------------------------------------------------
@dataclass(frozen=True)
class Config:
    seed: int = SEED
    model: ModelConfig = field(default_factory=ModelConfig)
    split: SplitConfig = field(default_factory=SplitConfig)
    train: TrainConfig = field(default_factory=TrainConfig)
    infer: InferConfig = field(default_factory=InferConfig)
    rag: RagConfig = field(default_factory=RagConfig)
    mongo: MongoConfig = field(default_factory=MongoConfig)
    teacher: TeacherConfig = field(default_factory=TeacherConfig)


CONFIG = Config()

# Task identifiers used throughout the pipeline.
TASKS = ("text2sql", "sql2nosql", "text2nosql")

# Prompt headers per task (plan.md §5).
TASK_HEADERS = {
    "text2sql": "[Task: NL-to-SQL]",
    "sql2nosql": "[Task: SQL-to-MQL]",
    "text2nosql": "[Task: NL-to-MQL]",
}

# Output split markers per task (plan.md §5).
OUTPUT_MARKERS = {
    "text2sql": "Corrected_SQL:",
    "sql2nosql": "Final_MQL:",
    "text2nosql": "Final_MQL:",
}


def ensure_dirs() -> None:
    """Create output directories if absent (safe to call repeatedly)."""
    for d in (MODELS_DIR, OUTPUTS_DIR, RETRIEVAL_INDEX_DIR, LOGS_DIR, SPLITS_DIR,
              FAILURES_DIR, AUGMENTED_DIR):
        d.mkdir(parents=True, exist_ok=True)
