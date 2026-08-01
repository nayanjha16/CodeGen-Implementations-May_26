"""
============================================================
RepoCoder Studio
schemas.py  —  v2
============================================================

Dataclass schemas for the Combined Stage pipeline.

v2 changes
----------
- ApprovedRow gains semantic_artifacts (parser-derived AST metadata,
  alignment evidence, structural features).
- New AlignmentRecord represents a candidate multilingual alignment
  produced by the Semantic Alignment Engine before corpus validation.
- EvidenceRecord represents one validated single-language artifact
  that feeds the alignment engine.
"""

from dataclasses import dataclass, asdict, field
from typing import Any, Dict, List, Optional


# ============================================================
# Evidence Layer (v2)
# ============================================================

@dataclass
class EvidenceRecord:
    """
    A single validated programming artifact in one language.

    Produced by the Record Validation stage.
    Feeds the Semantic Alignment Engine.
    """
    record_id: str               # deterministic ID from dataset + split + index
    dataset: str                 # source dataset (XLCoST, CodeXGLUE, ...)
    split: str                   # train / validation / test
    language: str                # "python" | "java" | "natural_language"
    content: str                 # the code or NL text
    natural_language: Optional[str]  # accompanying NL (if available, e.g. XLCoST)
    ast_metadata: Dict[str, Any] # parser-derived structural facts
    provenance: Dict[str, Any]   # dataset origin, version, adapter


# ============================================================
# Alignment Layer (v2)
# ============================================================

@dataclass
class AlignmentRecord:
    """
    A candidate multilingual alignment produced by the Semantic
    Alignment Engine.

    Contains all three modalities (NL, Python, Java) together with
    a confidence score and supporting evidence.  Still provisional —
    must pass Corpus Validation to become an ApprovedRow.
    """
    alignment_id: str
    natural_language: str
    python_code: str
    java_code: str
    confidence: float                  # [0, 1]
    alignment_strategy: str            # "title_match" | "embedding" | "cross_dataset"
    python_ast_metadata: Dict[str, Any]
    java_structural_metadata: Dict[str, Any]
    provenance: Dict[str, Any]
    split: str


# ============================================================
# Corpus schemas
# ============================================================

@dataclass
class CandidateRow:
    corpus_id: str
    dataset: str
    dataset_record_id: str
    split: str
    natural_language: Optional[str]
    python_code: str
    java_code: str
    metadata: Dict[str, Any]
    provenance: Dict[str, Any]


@dataclass
class ApprovedRow:
    corpus_id: str
    natural_language: str
    python_code: str
    java_code: str
    trusted_tests: Dict[str, Any]
    python_ast: Dict[str, Any]          # permanent Python AST artifacts (post-repair)
    java_parse_tree: Dict[str, Any]     # permanent Java parse tree artifacts (post-repair)
    csr_score: float                    # CSR similarity score (dynamic, not token bags)
    validation_status: str
    repair_history: List[Dict[str, Any]]
    corpus_version: str
    metadata: Dict[str, Any]
    provenance: Dict[str, Any]
    # parser-derived structural artifacts + alignment evidence (denormalized view)
    semantic_artifacts: Dict[str, Any] = field(default_factory=dict)


@dataclass
class RejectedRow:
    corpus_id: str
    dataset: str
    split: str
    reason: str
    details: Dict[str, Any]
    metadata: Dict[str, Any]
    provenance: Dict[str, Any]
    # v2: structured diagnostics from validation stages for post-rejection analysis
    validation_diagnostics: Dict[str, Any] = field(default_factory=dict)


@dataclass
class TrustedTest:
    test_id: str
    corpus_id: str
    input_data: Dict[str, Any]
    expected_output: Any
    source: str        # dataset / rule / teacher / manual
    status: str        # trusted / rejected / conflicting / insufficient
    metadata: Dict[str, Any]


@dataclass
class ValidationReport:
    corpus_id: str
    status: str
    python_status: str
    java_status: str
    trusted_test_status: str
    execution_status: str
    csr_status: str
    nl_status: str
    repair_history: List[Dict[str, Any]]
    details: Dict[str, Any]


@dataclass
class TaskExample:
    task_id: str
    corpus_id: str
    source_modality: str
    target_modality: str
    instruction: str
    input_text: str
    output_text: str
    split: str
    metadata: Dict[str, Any]


# ============================================================
# Utility
# ============================================================

def dataclass_to_dict(obj):
    """Deep-converts a dataclass to a plain dict (for serialization)."""
    return asdict(obj)
