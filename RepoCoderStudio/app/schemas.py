"""Pydantic request/response models for the RepoCoder Studio inference API."""

from typing import Any, Dict, List, Literal, Optional

from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    status: str
    device: str
    baseline_loaded: bool
    finetuned_loaded: bool
    finetuned_error: Optional[str] = None
    rag_loaded: bool = False
    rag_error: Optional[str] = None
    rag_mock_embeddings: Optional[bool] = None
    rag_corpus_loaded: bool = False
    rag_repo_path: Optional[str] = None
    operational_profile: str = "development"
    index_manifest_valid: Optional[bool] = None
    student_model: str
    adapter_name: str
    prompt_version: str
    repositories: Dict[str, Dict[str, Any]] = Field(default_factory=dict)


class TaskInfo(BaseModel):
    task_id: str
    source: str
    target: str
    description: str


class ShowcaseInfo(BaseModel):
    showcase_id: str
    repository_id: str = "generic"
    title: str
    task_id: str
    source_language: str
    target_language: str
    use_rag: bool
    capability: str
    description: str
    expected_sources: List[str] = Field(default_factory=list)
    source_path: Optional[str] = None
    input_text: str


class RepositoryInfo(BaseModel):
    repository_id: str
    title: str
    description: str
    languages: List[str]
    relative_path: Optional[str] = None
    rag_available: bool
    public_url: Optional[str] = None
    license: Optional[str] = None
    loaded: bool = False
    error: Optional[str] = None


class RetrievedSource(BaseModel):
    rank: Optional[int] = None
    name: str
    file_path: str
    component_type: str
    score: float
    dense_score: Optional[float] = None
    lexical_score: Optional[float] = None
    reranker_score: Optional[float] = None
    retrieval_method: str = "dense"
    provenance: str = "repository"


class GenerateRequest(BaseModel):
    task_id: str = Field(..., examples=["T1"])
    input_text: str = Field(default="", max_length=100000)
    model_type: Literal["baseline", "finetuned"] = "baseline"
    use_rag: bool = False
    repository_id: Literal["generic", "ledgerflow", "aws_s3"] = "generic"
    retry_invalid: bool = Field(
        default=False,
        description=(
            "Retry generation once when structural validation fails. "
            "The response explicitly reports whether a retry occurred."
        ),
    )


class GenerateResponse(BaseModel):
    task_id: str
    model_type: str
    repository_id: str = "generic"
    output: str
    rag_used: bool = False
    rag_decision: str = "not_requested"
    rag_top_score: Optional[float] = None
    retrieved_sources: list[RetrievedSource] = Field(default_factory=list)
    validation: Dict[str, Any] = Field(default_factory=dict)
    retried: bool = False
    first_output: Optional[str] = None
    first_validation: Optional[Dict[str, Any]] = None


class CompareRequest(BaseModel):
    task_id: str = Field(..., examples=["T1"])
    input_text: str = Field(default="", max_length=100000)
    use_rag: bool = False
    repository_id: Literal["generic", "ledgerflow", "aws_s3"] = "generic"
    retry_invalid: bool = Field(
        default=False,
        description=(
            "Retry each structurally invalid arm once. This is intended for "
            "interactive serving, not quantitative evaluation."
        ),
    )


class CompareResponse(BaseModel):
    task_id: str
    repository_id: str = "generic"
    baseline_output: str
    finetuned_output: Optional[str] = None
    finetuned_available: bool
    rag_used: bool = False
    rag_decision: str = "not_requested"
    rag_top_score: Optional[float] = None
    retrieved_sources: list[RetrievedSource] = Field(default_factory=list)
    baseline_validation: Dict[str, Any] = Field(default_factory=dict)
    finetuned_validation: Optional[Dict[str, Any]] = None
    baseline_retried: bool = False
    finetuned_retried: bool = False
    baseline_first_output: Optional[str] = None
    finetuned_first_output: Optional[str] = None
    baseline_first_validation: Optional[Dict[str, Any]] = None
    finetuned_first_validation: Optional[Dict[str, Any]] = None


class ReindexRequest(BaseModel):
    """repo_path must already exist on this server's mounted volume --
    this endpoint never clones or fetches anything remote. Get the repo
    onto the volume first (docker cp, a different volume mount, etc.)."""
    repo_path: str = Field(..., examples=["/data/repos/my-other-repo"])
    rebuild_corpus: bool = Field(
        default=False,
        description="Also rebuild the Stage 5 CorpusIndex (outputs/approved_corpus/approved_corpus.jsonl). "
        "Usually unnecessary -- the corpus index doesn't depend on which repo is indexed.",
    )


class ReindexResponse(BaseModel):
    status: str
    repo_path: str
    files: int
    functions: int
    classes: int
    mock_embeddings: bool
    migration_status: Optional[Dict[str, Any]] = None
    corpus_rows_indexed: Optional[int] = None
