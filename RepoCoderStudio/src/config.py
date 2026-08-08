"""
============================================================
RepoCoder Studio
config.py
============================================================

Central configuration module for RepoCoder Studio Combined Stage.

This file defines every runtime setting used by the project.

Design rule
-----------
No magic numbers should be scattered across the codebase.
All important paths, dataset names, limits, model names,
training settings, validation thresholds, and resume behavior
must come from this module.

Engineering Specification
-------------------------
Related sections:
- Section 3: Architecture
- Section 5: Corpus Construction
- Section 6: Corpus Validation
- Section 8: Unified Training Framework
- Section 9: Evaluation Framework
- Section 10: Software Architecture

Stage Learnings
---------------
Stage 1:
    Configuration was spread across notebook cells, making it hard
    to reproduce runs.

Stage 2:
    Dataset and evaluation changes required many manual edits.

Stage 3:
    Runtime restarts and dataset loader failures showed that all
    storage, resume, and dataset behavior must be centralized.

Author
------
RepoCoder Studio
"""

# ============================================================
# Imports
# ============================================================

import os
import random
import time
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

# ============================================================
# 1. Global project constants
# ============================================================

PROJECT_NAME = "RepoCoderStudio"
PROJECT_STAGE = "CombinedStage"
SPEC_VERSION = "2.0"

DEFAULT_RANDOM_SEED = 42




# ============================================================
# 1b. Project metadata configuration
# ============================================================

@dataclass(frozen=True)
class ProjectConfig:
    """
    Project identity metadata.

    This section exists so downstream manifests, reports, and evaluation
    artifacts do not rely on hard-coded project strings or notebook-local
    constants.
    """

    name: str = PROJECT_NAME
    stage: str = PROJECT_STAGE
    specification_version: str = SPEC_VERSION


# ============================================================
# 1c. Experiment metadata configuration
# ============================================================

@dataclass(frozen=True)
class ExperimentConfig:
    """
    Version identifiers used in manifests and reproducibility reports.

    These values centralize prompt, task, metric, and manifest versions so
    notebooks and modules do not scatter version strings across the codebase.
    """

    experiment_version: str = "experiment_v2.6"
    prompt_version: str = os.environ.get(
        "REPOCODER_PROMPT_VERSION", "prompt_contract_v2.6"
    )
    task_contract_version: str = "task_contract_v2.6"
    task_builder_version: str = "task_builder_v2.3"
    task_registry_version: str = "task_registry_v2.0"
    metric_registry_version: str = "metric_registry_v2.0"
    # v2.7 fingerprints the run profile, data limits, and training settings,
    # so a small demo checkpoint cannot be resumed by a capstone run.
    training_manifest_version: str = os.environ.get(
        "REPOCODER_TRAINING_MANIFEST_VERSION", "training_manifest_v2.7"
    )

# ============================================================
# 2. Runtime mode configuration
# ============================================================

@dataclass(frozen=True)
class RuntimeConfig:
    """
    Runtime behavior configuration.

    Fields
    ------
    run_mode:
        One of "demo", "capstone", or "full".

        demo:
            Small dataset limits, fast debugging, shorter training.

        capstone:
            Mentor-facing run with enough training/retrieval examples for a
            meaningful result while remaining practical on a Colab T4.

        full:
            Larger dataset use, longer training, production-style run.

    use_google_drive:
        If True, the project root is expected to live in Google Drive.

    auto_resume:
        If True, the pipeline tries to reuse existing artifacts before
        recomputing expensive stages.

    overwrite_existing:
        If True, existing artifacts may be overwritten.
        Keep False during normal development.

    random_seed:
        Global seed used for reproducibility.
    """

    run_mode: str = os.environ.get("REPOCODER_RUN_MODE", "demo").lower()
    use_google_drive: bool = True
    auto_resume: bool = True
    overwrite_existing: bool = False
    random_seed: int = DEFAULT_RANDOM_SEED

    def validate(self):
        assert self.run_mode in {"demo", "capstone", "full"}, (
            "run_mode must be one of 'demo', 'capstone', or 'full'"
        )


# ============================================================
# 3. Storage configuration
# ============================================================

@dataclass(frozen=True)
class StorageConfig:
    """
    Storage and project folder configuration.

    Important
    ---------
    Google Drive is the primary storage location because Colab
    sessions are temporary.

    This prevents loss of:
    - candidate corpus
    - approved corpus
    - rejected corpus
    - validation reports
    - checkpoints
    - final LoRA adapters
    - evaluation outputs
    """

    drive_mount_point: str = "/content/drive"
    drive_project_root: str = os.environ.get(
        "REPOCODER_PROJECT_ROOT", "/content/drive/MyDrive/RepoCoderStudio"
    )

    notebooks_dir: str = "notebooks"
    src_dir: str = "src"
    configs_dir: str = "configs"
    datasets_dir: str = "datasets"
    outputs_dir: str = "outputs"

    candidate_corpus_dir: str = "outputs/candidate_corpus"
    approved_corpus_dir: str = "outputs/approved_corpus"
    rejected_corpus_dir: str = "outputs/rejected_corpus"
    trusted_tests_dir: str = "outputs/trusted_tests"
    task_datasets_dir: str = "outputs/task_datasets"
    checkpoints_dir: str = "outputs/checkpoints"
    adapters_dir: str = "outputs/adapters"
    evaluation_dir: str = "outputs/evaluation"
    reports_dir: str = "outputs/reports"
    logs_dir: str = "outputs/logs"
    manifests_dir: str = "outputs/manifests"

    # Stage 4 -- repository index + embeddings (data artifacts, not reports;
    # the human-readable Stage 4/5 summaries derived from them live under
    # reports_dir, same split as every other stage's raw vs. report outputs).
    repo_explorer_output_dir: str = "outputs/repo_explorer/output"
    repo_explorer_embedding_dir: str = "outputs/repo_explorer/embeddings"

    # Stage 5 -- FAISS index built directly over approved_corpus.jsonl's
    # train-split rows (see src/corpus_retriever.py), a second RAG source
    # alongside the Stage 4 repository index.
    corpus_index_dir: str = "outputs/corpus_index"

    def project_root(self) -> Path:
        return Path(self.drive_project_root)

    def resolve(self, relative_path: str) -> Path:
        return self.project_root() / relative_path


# ============================================================
# 4. Dataset configuration
# ============================================================

@dataclass(frozen=True)
class DatasetConfig:
    """
    Dataset configuration.

    Dataset strategy
    ----------------
    XLCoST:
        Mandatory primary dataset.

    CodeXGLUE:
        Secondary evidence source for code-to-text rows.

    AVATAR / TransCoder:
        Removed from the finalized v2 implementation.
    """

    use_xlcost: bool = True
    use_codexglue: bool = True   # Google CodeXGLUE Code-to-Text (second evidence source)

    xlcost_dataset_name: str = "codeparrot/xlcost-text-to-code"
    xlcost_python_config: str = "Python-program-level"
    xlcost_java_config: str = "Java-program-level"

    # Finalized dataset target. Fallback is kept for Colab/HF compatibility.
    codexglue_dataset_name: str = "google/code_x_glue_ct_code_to_text"
    codexglue_fallback_dataset_name: str = "code_search_net"
    codexglue_python_config: str = "python"
    codexglue_java_config: str = "java"


    # Dataset cache settings (v2: persistent cache prevents re-downloads)
    dataset_cache_enabled: bool = True
    dataset_cache_dir: str = "datasets/cache"

    # The fast notebook owns these through environment variables. Keeping the
    # defaults here preserves the ordinary demo profile for CLI/API users and
    # leaves the capstone profile completely unchanged.
    demo_train_limit: int = int(
        os.environ.get("REPOCODER_DEMO_TRAIN_LIMIT", "300")
    )
    demo_validation_limit: int = int(
        os.environ.get("REPOCODER_DEMO_VALIDATION_LIMIT", "60")
    )
    demo_test_limit: int = int(
        os.environ.get("REPOCODER_DEMO_TEST_LIMIT", "60")
    )

    # A larger, still Colab-practical corpus. Unlike simply indexing
    # validation/test rows, this expands only the train pool and therefore
    # preserves the retrieval leakage boundary.
    capstone_train_limit: int = int(
        os.environ.get("REPOCODER_CAPSTONE_TRAIN_LIMIT", "1200")
    )
    capstone_validation_limit: int = int(
        os.environ.get("REPOCODER_CAPSTONE_VALIDATION_LIMIT", "150")
    )
    capstone_test_limit: int = int(
        os.environ.get("REPOCODER_CAPSTONE_TEST_LIMIT", "150")
    )

    full_train_limit: Optional[int] = None
    full_validation_limit: Optional[int] = None
    full_test_limit: Optional[int] = None

    expected_splits: Tuple[str, ...] = ("train", "validation", "test")

    def get_split_limit(self, split: str, run_mode: str) -> Optional[int]:
        """
        Returns the configured row limit for a dataset split.

        Parameters
        ----------
        split:
            Dataset split name.

        run_mode:
            demo or full.

        Returns
        -------
        Optional[int]
            Maximum number of rows to use, or None for full split.
        """

        split = split.lower()

        if run_mode == "full":
            if split == "train":
                return self.full_train_limit
            if split in {"validation", "valid", "dev"}:
                return self.full_validation_limit
            if split == "test":
                return self.full_test_limit
            return None

        if run_mode == "capstone":
            if split == "train":
                return self.capstone_train_limit
            if split in {"validation", "valid", "dev"}:
                return self.capstone_validation_limit
            if split == "test":
                return self.capstone_test_limit
            return self.capstone_train_limit

        if split == "train":
            return self.demo_train_limit
        if split in {"validation", "valid", "dev"}:
            return self.demo_validation_limit
        if split == "test":
            return self.demo_test_limit

        return self.demo_train_limit


# ============================================================
# 5. Corpus configuration
# ============================================================

@dataclass(frozen=True)
class CorpusConfig:
    """
    Corpus construction configuration.

    Candidate Corpus:
        Rows after dataset loading and schema normalization.

    Approved Corpus:
        Rows that pass validation and can be used for task generation.

    Rejected Corpus:
        Rows excluded from training with reasons.
    """

    corpus_version: str = "combined_stage_v2.0"

    enable_deduplication: bool = True
    remove_exact_duplicates: bool = True
    remove_structural_duplicates: bool = True

    min_python_chars: int = 20
    min_java_chars: int = 20
    min_nl_words: int = 4

    save_candidate_corpus: bool = True
    save_duplicate_report: bool = True
    save_corpus_statistics: bool = True


# ============================================================
# 5b. Alignment configuration (v2)
# ============================================================

@dataclass(frozen=True)
class AlignmentConfig:
    """
    Semantic Alignment Engine configuration.

    v2 replaces positional split-index alignment with semantic alignment.

    Strategy
    --------
    Within a single dataset (e.g. XLCoST):
        Normalize the NL description field and match Python/Java records
        sharing the same normalized description key. This is fast and
        deterministic and replicates the Stage 3 title-based fix.

    Cross-dataset:
        Use sentence-transformer embeddings + cosine similarity to
        retrieve the top-K candidates, then score with structural evidence.
        Only pairs exceeding confidence_threshold are accepted.

    use_embedding_alignment:
        When True, sentence-transformers are used for cross-dataset
        alignment. When False or when the library is unavailable,
        only normalized-title matching is used.
    """

    use_embedding_alignment: bool = True
    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    alignment_top_k: int = 10
    confidence_threshold: float = 0.50

    # Structural bonus added to confidence when function-count similarity
    # is high (Python function count ≈ Java method count)
    structural_bonus: float = 0.10

    # Within-dataset title match always receives confidence = 1.0
    within_dataset_confidence: float = 1.0


# ============================================================
# 6. Validation configuration
# ============================================================

@dataclass(frozen=True)
class ValidationConfig:
    """
    Corpus validation configuration.

    Validation principle
    --------------------
    Every imported row is untrusted until validated.

    Execution validation is allowed to return NOT_FEASIBLE when no
    safe generic test harness is available. This follows the frozen
    engineering design.
    """

    enable_python_validation: bool = True
    enable_java_validation: bool = True
    enable_trusted_test_builder: bool = True
    enable_execution_validation: bool = True
    enable_csr_validation: bool = True
    enable_nl_validation: bool = True

    allow_execution_not_feasible: bool = True

    # v2: CSR threshold relaxed — CSR is now supporting evidence, not gate
    min_csr_similarity: float = 0.20

    max_repair_attempts_per_component: int = 3

    enable_nl_repair: bool = True
    enable_python_repair: bool = True
    enable_java_wrapper_repair: bool = True
    enable_teacher_repair: bool = True   # v2.5: keep bounded Teacher repair enabled during validation
    enable_teacher_test_generation: bool = False
    enable_teacher_completion_queue_processing: bool = False
    teacher_repair_only_generated_modalities: bool = True

    java_compile_timeout_seconds: int = 10
    python_parse_timeout_seconds: int = 5
    max_execution_tests_per_row: int = 5

    # v2: Use Tree-sitter for Java structural analysis (falls back to regex)
    use_tree_sitter_java: bool = True


# ============================================================
# 7. Model configuration
# ============================================================

@dataclass(frozen=True)
class ModelConfig:
    """
    Model configuration.

    Student model:
        Fine-tuned using LoRA.

    Teacher model:
        Used for bounded repair/completion when validation fails.
        The repair loop remains enabled and capped by max_repair_attempts_per_component.
        Larger than the student on purpose -- a stronger teacher is more
        likely to produce a repaired NL/Python/Java fragment that actually
        passes the deterministic validator on retry. Loaded in 4-bit
        (use_4bit=True below) since it only runs when a GPU is available.
    """

    student_model_name: str = os.environ.get(
        "REPOCODER_STUDENT_MODEL", "Qwen/Qwen2.5-Coder-0.5B-Instruct"
    )
    teacher_model_name: str = os.environ.get(
        "REPOCODER_TEACHER_MODEL", "Qwen/Qwen2.5-Coder-7B-Instruct"
    )

    use_4bit: bool = True
    use_flash_attention: bool = False

    max_seq_length: int = 1024
    max_new_tokens: int = 384
    nl_max_new_tokens: int = int(
        os.environ.get("REPOCODER_NL_MAX_NEW_TOKENS", "160")
    )
    generation_repetition_penalty: float = float(
        os.environ.get("REPOCODER_REPETITION_PENALTY", "1.08")
    )


# ============================================================
# 8. Training configuration
# ============================================================

@dataclass(frozen=True)
class TrainingConfig:
    """
    LoRA training configuration.

    Stage learning
    --------------
    Stage 2 and Stage 3 showed that Colab training must be
    checkpointed aggressively and stored in Drive.
    """

    enable_training: bool = True

    num_train_epochs_demo: float = 1.0
    # The capstone profile has roughly four times the raw training rows of the
    # demo. One completion-masked pass supplies more useful target tokens than
    # the old two-pass demo-style schedule while reducing overfitting.
    num_train_epochs_capstone: float = 1.0
    num_train_epochs_full: float = 2.0

    per_device_train_batch_size: int = 1
    gradient_accumulation_steps: int = 8

    # A less aggressive rate is safer for the larger multi-task corpus and
    # helps preserve the coder base model's existing capability.
    learning_rate: float = float(
        os.environ.get("REPOCODER_LEARNING_RATE", "1e-4")
    )
    warmup_ratio: float = 0.03
    weight_decay: float = 0.0

    # Slightly more adapter capacity for six heterogeneous tasks.
    lora_rank: int = 16
    lora_alpha: int = 32
    lora_dropout: float = 0.05

    logging_steps: int = 10
    save_steps_demo: int = 50
    save_steps_full: int = 100

    save_total_limit: int = 3
    auto_resume_from_checkpoint: bool = True

    # v2.4 prompt/task-interference controls
    use_task_contract_prompts: bool = True
    demo_task_cap_per_split: int = 10000

    final_adapter_name: str = os.environ.get(
        "REPOCODER_ADAPTER_NAME", "RepoCoderStudio_RAGAware_LoRA_v1_3_transform"
    )

    # The checkpoint fingerprint must hash the dataset that is actually fed
    # to training. RAG-aware retraining uses a separate rendered dataset.
    task_dataset_filename: str = os.environ.get(
        "REPOCODER_TRAINING_DATASET_FILENAME", "task_dataset.jsonl"
    )


# ============================================================
# 9. Evaluation configuration
# ============================================================

@dataclass(frozen=True)
class EvaluationConfig:
    """
    Evaluation configuration.

    Metrics are selected by task type through the Metric Registry.

    Code tasks:
        - parse/compile
        - execution where feasible
        - official CodeBLEU when available
        - CSR score
        - CodeBLEU-lite diagnostic fallback

    NL tasks:
        - ROUGE-L
        - SacreBLEU
        - semantic similarity diagnostic
    """

    enable_evaluation: bool = True

    # The previous ten-row setting produced unstable percentages (one row
    # changed a task score by ten points). The capstone notebook evaluates
    # all 50 held-out rows per task by default. Override for a quick smoke
    # run without editing source.
    demo_eval_examples_per_task: int = int(
        os.environ.get("REPOCODER_EVAL_EXAMPLES_PER_TASK", "50")
    )
    full_eval_examples_per_task: int = int(
        os.environ.get("REPOCODER_FULL_EVAL_EXAMPLES_PER_TASK", "100")
    )
    # Fifty paired rows make per-task routing less sensitive to one or two
    # examples than the previous 20-row pilot. Generation is performed once;
    # bootstrap stability below reuses the saved validation rows.
    rag_tuning_examples_per_task: int = int(
        os.environ.get("REPOCODER_RAG_TUNING_EXAMPLES_PER_TASK", "50")
    )
    rag_tuning_top_k_candidates: Tuple[int, ...] = (1, 2)
    rag_policy_min_delta: float = float(
        os.environ.get("REPOCODER_RAG_POLICY_MIN_DELTA", "0.01")
    )
    rag_policy_bootstrap_samples: int = int(
        os.environ.get("REPOCODER_RAG_POLICY_BOOTSTRAP_SAMPLES", "2000")
    )
    rag_policy_bootstrap_seed: int = int(
        os.environ.get("REPOCODER_RAG_POLICY_BOOTSTRAP_SEED", "42")
    )
    rag_policy_confidence_level: float = float(
        os.environ.get("REPOCODER_RAG_POLICY_CONFIDENCE_LEVEL", "0.95")
    )
    rag_policy_min_positive_probability: float = float(
        os.environ.get("REPOCODER_RAG_POLICY_MIN_POSITIVE_PROBABILITY", "0.80")
    )
    rag_policy_min_selection_stability: float = float(
        os.environ.get("REPOCODER_RAG_POLICY_MIN_SELECTION_STABILITY", "0.70")
    )

    save_prediction_logs: bool = True
    save_metric_rows: bool = True
    save_summary_reports: bool = True

    # Comparison engine: delta below this value is flagged as a regression
    regression_threshold: float = -0.02


# ============================================================
# 10. Logging configuration
# ============================================================

@dataclass(frozen=True)
class RetrievalConfig:
    """
    Stage 4/5 configuration -- repository understanding and RAG.

    Design rule
    -----------
    Index-building (Stage 4) happens offline, same as LoRA training.
    The inference container only ever loads pre-built artifacts here --
    it never re-indexes a repository at request time.
    """

    enable_retrieval: bool = os.environ.get("REPOCODER_ENABLE_RAG", "true").lower() == "true"

    # The repository being indexed for retrieval. Ships with a bundled
    # sample repo (repo_explorer_data/sample_repo, relative to the app's
    # working directory) — point this at a real codebase to index that
    # instead.
    repo_path: str = os.environ.get("REPOCODER_REPO_PATH", "repo_explorer_data/sample_repo")

    # Build artifact *locations* (repo_index.json, embeddings, FAISS indices)
    # live on StorageConfig (repo_explorer_output_dir / repo_explorer_embedding_dir),
    # same as adapters_dir / checkpoints_dir / evaluation_dir -- every output
    # path is centralized there so ProjectStorageManager.initialize_project()
    # provisions it upfront and print_project_status() can report on it.

    embedding_model: str = os.environ.get(
        "REPOCODER_EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2"
    )
    top_k: int = 5
    candidate_pool_size: int = 20
    max_snippet_chars: int = 1600
    max_context_chars: int = int(
        os.environ.get("REPOCODER_MAX_CONTEXT_CHARS", "7000")
    )
    # Quantitative corpus-RAG evaluation deliberately uses compact top-1
    # evidence by default. A 0.5B model with a 1024-token window is easily
    # distracted by five full exemplars even when each is relevant.
    corpus_eval_top_k: int = int(
        os.environ.get("REPOCODER_CORPUS_EVAL_TOP_K", "1")
    )
    min_similarity: float = 0.20
    # Hybrid retrieval combines dense similarity with identifier/token overlap.
    # This improves exact API/symbol queries without requiring a second model.
    enable_hybrid_retrieval: bool = (
        os.environ.get("REPOCODER_ENABLE_HYBRID_RETRIEVAL", "true").lower() == "true"
    )
    dense_score_weight: float = float(
        os.environ.get("REPOCODER_DENSE_SCORE_WEIGHT", "0.75")
    )
    lexical_score_weight: float = float(
        os.environ.get("REPOCODER_LEXICAL_SCORE_WEIGHT", "0.25")
    )
    # Cross-encoder reranking is enabled by default so the notebook's
    # hybrid-vs-cross-encoder ablation exercises a real third arm without
    # requiring a late environment mutation after CONFIG has already been
    # imported. Set REPOCODER_RERANKER_MODEL="" to disable it for
    # latency-sensitive deployments.
    reranker_model: str = os.environ.get(
        "REPOCODER_RERANKER_MODEL",
        "cross-encoder/ms-marco-MiniLM-L-6-v2",
    )
    reranker_weight: float = float(os.environ.get("REPOCODER_RERANKER_WEIGHT", "0.35"))
    # RAG abstains when evidence is weak or ambiguous instead of forcing noisy
    # context into every eligible generation.
    rag_min_top_score: float = float(
        os.environ.get("REPOCODER_RAG_MIN_TOP_SCORE", "0.28")
    )
    rag_min_score_margin: float = float(
        os.environ.get("REPOCODER_RAG_MIN_SCORE_MARGIN", "0.015")
    )
    rag_allow_ambiguous_multi_source: bool = (
        os.environ.get("REPOCODER_RAG_ALLOW_AMBIGUOUS_MULTI_SOURCE", "true").lower()
        == "true"
    )
    enable_dependency_expansion: bool = True
    max_dependency_results: int = 2
    enable_hierarchical_expansion: bool = True
    max_caller_results: int = 2
    max_dependent_results: int = 2
    allow_mock_embeddings: bool = (
        os.environ.get("REPOCODER_ALLOW_MOCK_EMBEDDINGS", "false").lower() == "true"
    )
    operational_profile: str = os.environ.get(
        "REPOCODER_PROFILE", "development"
    ).lower()

    # Stage 5 -- persist every retrieval call to
    # outputs/reports/retrieval_query_log.jsonl as it happens (same
    # "report every stage produces" rule as validation_report.jsonl /
    # alignment_analytics.jsonl). Disable for a high-traffic inference
    # server if the query log isn't wanted.
    log_retrieval_queries: bool = (
        os.environ.get("REPOCODER_LOG_RETRIEVAL_QUERIES", "false").lower() == "true"
    )

    # All six tasks may use retrieval. RetrievalEngine routes each one to a
    # modality-aligned corpus query-key index: natural language for T1/T2,
    # Python for T3/T5, and Java for T4/T6.
    rag_eligible_tasks: Tuple[str, ...] = ("T1", "T2", "T3", "T4", "T5", "T6")

    # Deployed-service capability: point the running server at a different
    # repository without redeploying the container. POST /api/admin/reindex
    # (app/main.py), gated by this shared-secret token. None (unset) means
    # the endpoint is disabled -- a public deployment doesn't get an admin
    # surface just because it exists in the code; it has to be turned on
    # on purpose. The endpoint only ever re-indexes a path already present
    # on this server's mounted volume -- it never clones or fetches
    # anything remote, so there's no SSRF-style surface here even when enabled.
    admin_reindex_token: Optional[str] = os.environ.get("REPOCODER_ADMIN_TOKEN") or None
    allowed_repo_root: str = os.environ.get("REPOCODER_ALLOWED_REPO_ROOT", "/data/repos")
    enable_online_reindex: bool = (
        os.environ.get("REPOCODER_ENABLE_ONLINE_REINDEX", "false").lower() == "true"
    )


@dataclass(frozen=True)
class LoggingConfig:
    """
    Logging configuration.

    Logs are saved to Drive so debugging survives runtime restarts.
    """

    log_to_console: bool = True
    log_to_file: bool = True
    log_level: str = "INFO"
    log_filename: str = "repocoder_combined_stage.log"


@dataclass(frozen=True)
class ServingConfig:
    """Online inference safety and capacity controls."""

    api_key: Optional[str] = os.environ.get("REPOCODER_API_KEY") or None
    max_input_chars: int = int(os.environ.get("REPOCODER_MAX_INPUT_CHARS", "100000"))
    max_concurrent_generations: int = int(
        os.environ.get("REPOCODER_MAX_CONCURRENT_GENERATIONS", "1")
    )


# ============================================================
# 11. Main application configuration
# ============================================================

@dataclass(frozen=True)
class AppConfig:
    """
    Root configuration object.

    Every module should receive this object or one of its child
    configs instead of defining its own constants.
    """

    project: ProjectConfig = ProjectConfig()
    experiment: ExperimentConfig = ExperimentConfig()
    runtime: RuntimeConfig = RuntimeConfig()
    storage: StorageConfig = StorageConfig()
    dataset: DatasetConfig = DatasetConfig()
    corpus: CorpusConfig = CorpusConfig()
    alignment: AlignmentConfig = AlignmentConfig()
    validation: ValidationConfig = ValidationConfig()
    models: ModelConfig = ModelConfig()
    training: TrainingConfig = TrainingConfig()
    evaluation: EvaluationConfig = EvaluationConfig()
    retrieval: RetrievalConfig = RetrievalConfig()
    logging: LoggingConfig = LoggingConfig()
    serving: ServingConfig = ServingConfig()

    def validate(self):
        """
        Validates the complete configuration.

        Raises
        ------
        AssertionError
            If any configuration value is invalid.
        """

        self.runtime.validate()

        assert self.project.name, "Project name must not be empty"
        assert self.project.stage, "Project stage must not be empty"
        assert self.project.specification_version, "Specification version must not be empty"
        assert self.experiment.prompt_version, "Prompt version must not be empty"
        assert self.experiment.task_contract_version, "Task contract version must not be empty"

        assert self.dataset.use_xlcost is True, (
            "XLCoST must remain enabled because it is the mandatory primary corpus."
        )

        assert 0.0 <= self.alignment.confidence_threshold <= 1.0
        assert self.alignment.alignment_top_k >= 1

        assert self.corpus.min_python_chars > 0
        assert self.corpus.min_java_chars > 0
        assert self.corpus.min_nl_words > 0

        assert 0.0 <= self.validation.min_csr_similarity <= 1.0

        assert self.training.per_device_train_batch_size >= 1
        assert self.training.gradient_accumulation_steps >= 1
        assert self.training.num_train_epochs_demo > 0
        assert self.training.num_train_epochs_capstone > 0
        assert self.training.num_train_epochs_full > 0
        assert self.training.learning_rate > 0
        assert self.training.lora_rank > 0
        assert self.training.lora_alpha > 0
        assert Path(self.training.task_dataset_filename).name == self.training.task_dataset_filename, (
            "task_dataset_filename must be a filename inside outputs/task_datasets"
        )

        assert self.models.max_seq_length > 0
        assert self.models.max_new_tokens > 0
        assert self.models.nl_max_new_tokens > 0
        assert self.models.generation_repetition_penalty >= 1.0
        assert self.dataset.capstone_train_limit >= 1
        assert self.dataset.capstone_validation_limit >= 1
        assert self.dataset.capstone_test_limit >= 1
        assert self.evaluation.demo_eval_examples_per_task >= 1
        assert self.evaluation.rag_tuning_examples_per_task >= 1
        assert all(k >= 1 for k in self.evaluation.rag_tuning_top_k_candidates)
        assert self.evaluation.rag_policy_min_delta >= 0.0
        assert self.evaluation.rag_policy_bootstrap_samples >= 100
        assert 0.0 < self.evaluation.rag_policy_confidence_level < 1.0
        assert 0.0 <= self.evaluation.rag_policy_min_positive_probability <= 1.0
        assert 0.0 <= self.evaluation.rag_policy_min_selection_stability <= 1.0
        assert self.retrieval.operational_profile in {"development", "evaluation", "production"}
        assert self.retrieval.top_k >= 1
        assert self.retrieval.corpus_eval_top_k >= 1
        assert self.retrieval.candidate_pool_size >= self.retrieval.top_k
        assert -1.0 <= self.retrieval.min_similarity <= 1.0
        assert 0.0 <= self.retrieval.dense_score_weight <= 1.0
        assert 0.0 <= self.retrieval.lexical_score_weight <= 1.0
        assert self.retrieval.dense_score_weight + self.retrieval.lexical_score_weight > 0
        assert 0.0 <= self.retrieval.reranker_weight <= 1.0
        assert -1.0 <= self.retrieval.rag_min_top_score <= 1.0
        assert self.retrieval.rag_min_score_margin >= 0.0
        assert self.serving.max_input_chars >= 1
        assert self.serving.max_concurrent_generations >= 1

    def to_dict(self) -> Dict[str, Any]:
        """
        Converts configuration to dictionary.

        Useful for:
        - saving config snapshot
        - run manifest
        - reproducibility reports
        """

        return asdict(self)


# ============================================================
# 12. Global CONFIG object
# ============================================================

CONFIG = AppConfig()
CONFIG.validate()


# ============================================================
# 13. Helper functions
# ============================================================

def set_global_seed(seed: int = DEFAULT_RANDOM_SEED):
    """
    Sets global random seed.

    This function intentionally avoids importing heavy libraries
    unless they are available.

    Parameters
    ----------
    seed:
        Random seed.
    """

    random.seed(seed)
    os.environ["PYTHONHASHSEED"] = str(seed)

    try:
        import numpy as np
        np.random.seed(seed)
    except Exception:
        pass

    try:
        import torch
        torch.manual_seed(seed)
        if torch.cuda.is_available():
            torch.cuda.manual_seed_all(seed)
    except Exception:
        pass


def get_run_id(config: AppConfig = CONFIG) -> str:
    """
    Creates a deterministic-style run identifier using timestamp
    and runtime mode.

    Returns
    -------
    str
        Example:
        Run_20260627_153012_demo
    """

    timestamp = time.strftime("%Y%m%d_%H%M%S")
    return f"Run_{timestamp}_{config.runtime.run_mode}"


def print_config_summary(config: AppConfig = CONFIG):
    """
    Prints a human-readable configuration summary.

    This is useful in notebooks so the user can confirm the run mode,
    dataset settings, model, checkpoint behavior, and storage path before
    starting expensive steps.
    """

    print("=" * 72)
    print("RepoCoder Studio — Combined Stage Configuration")
    print("=" * 72)
    print(f"Project                 : {config.project.name}")
    print(f"Stage                   : {config.project.stage}")
    print(f"Specification Version   : {config.project.specification_version}")
    print(f"Run Mode                : {config.runtime.run_mode}")
    print(f"Google Drive Enabled    : {config.runtime.use_google_drive}")
    print(f"Auto Resume             : {config.runtime.auto_resume}")
    print(f"Project Root            : {config.storage.drive_project_root}")
    print("-" * 72)
    print("Primary Dataset         : XLCoST")
    print(f"XLCoST Dataset          : {config.dataset.xlcost_dataset_name}")
    print(f"Python Config           : {config.dataset.xlcost_python_config}")
    print(f"Java Config             : {config.dataset.xlcost_java_config}")
    print(f"CodeXGLUE Enabled       : {config.dataset.use_codexglue}")
    print(f"Dataset Cache           : {config.dataset.dataset_cache_enabled}")
    print(f"Alignment Strategy      : {'semantic+embedding' if config.alignment.use_embedding_alignment else 'normalized-title'}")
    print(f"Alignment Threshold     : {config.alignment.confidence_threshold}")
    print(f"Tree-sitter Java        : {config.validation.use_tree_sitter_java}")
    print("-" * 72)
    print(f"Student Model           : {config.models.student_model_name}")
    print(f"Max Sequence Length     : {config.models.max_seq_length}")
    print(f"4-bit Loading           : {config.models.use_4bit}")
    print(f"Embedding Model         : {config.retrieval.embedding_model}")
    print(f"Cross-Encoder Reranker  : {config.retrieval.reranker_model or 'disabled'}")
    print("-" * 72)
    print(f"Training Enabled        : {config.training.enable_training}")
    print(f"Auto Checkpoint Resume  : {config.training.auto_resume_from_checkpoint}")
    print(f"Final Adapter Name      : {config.training.final_adapter_name}")
    print(f"Training Dataset        : {config.training.task_dataset_filename}")
    print(f"Prompt Version          : {config.experiment.prompt_version}")
    print("=" * 72)


# ============================================================
# 14. Initialize seed immediately
# ============================================================

set_global_seed(CONFIG.runtime.random_seed)
