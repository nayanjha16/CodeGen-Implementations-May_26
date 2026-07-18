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

from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Optional, Tuple, Dict, Any
import os
import time
import random


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
    prompt_version: str = "prompt_contract_v2.6"
    task_contract_version: str = "task_contract_v2.6"
    task_builder_version: str = "task_builder_v2.3"
    task_registry_version: str = "task_registry_v2.0"
    metric_registry_version: str = "metric_registry_v2.0"
    training_manifest_version: str = "training_manifest_v2.6"

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
        Either "demo" or "full".

        demo:
            Small dataset limits, fast debugging, shorter training.

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

    run_mode: str = "demo"
    use_google_drive: bool = True
    auto_resume: bool = True
    overwrite_existing: bool = False
    random_seed: int = DEFAULT_RANDOM_SEED

    def validate(self):
        assert self.run_mode in {"demo", "full"}, (
            "run_mode must be either 'demo' or 'full'"
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

    demo_train_limit: int = 300
    demo_validation_limit: int = 60
    demo_test_limit: int = 60

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
    """

    student_model_name: str = os.environ.get(
        "REPOCODER_STUDENT_MODEL", "Qwen/Qwen2.5-Coder-0.5B-Instruct"
    )
    teacher_model_name: str = os.environ.get(
        "REPOCODER_TEACHER_MODEL", "Qwen/Qwen2.5-Coder-0.5B-Instruct"
    )

    use_4bit: bool = True
    use_flash_attention: bool = False

    max_seq_length: int = 1024
    max_new_tokens: int = 384


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
    num_train_epochs_full: float = 2.0

    per_device_train_batch_size: int = 1
    gradient_accumulation_steps: int = 8

    learning_rate: float = 2e-4
    warmup_ratio: float = 0.03
    weight_decay: float = 0.0

    lora_rank: int = 8
    lora_alpha: int = 16
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
        "REPOCODER_ADAPTER_NAME", "RepoCoderStudio_CombinedStage_LoRA_v1_0"
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

    demo_eval_examples_per_task: int = 10
    full_eval_examples_per_task: int = 100

    save_prediction_logs: bool = True
    save_metric_rows: bool = True
    save_summary_reports: bool = True

    # Comparison engine: delta below this value is flagged as a regression
    regression_threshold: float = -0.02


# ============================================================
# 10. Logging configuration
# ============================================================

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
    logging: LoggingConfig = LoggingConfig()

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
        assert self.training.learning_rate > 0
        assert self.training.lora_rank > 0
        assert self.training.lora_alpha > 0

        assert self.models.max_seq_length > 0
        assert self.models.max_new_tokens > 0

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
    print(f"Primary Dataset         : XLCoST")
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
    print("-" * 72)
    print(f"Training Enabled        : {config.training.enable_training}")
    print(f"Auto Checkpoint Resume  : {config.training.auto_resume_from_checkpoint}")
    print(f"Final Adapter Name      : {config.training.final_adapter_name}")
    print(f"Prompt Version          : {config.experiment.prompt_version}")
    print("=" * 72)


# ============================================================
# 14. Initialize seed immediately
# ============================================================

set_global_seed(CONFIG.runtime.random_seed)