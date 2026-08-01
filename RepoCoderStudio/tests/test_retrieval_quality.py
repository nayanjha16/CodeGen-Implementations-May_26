from dataclasses import dataclass

# Keep this module dependency-light: no torch/faiss/sentence-transformers.
from src.retrieval_quality import code_tokens, decide_rag, hybrid_rerank, lexical_overlap


@dataclass
class Result:
    score: float
    name: str
    file_path: str
    source_preview: str
    component_type: str = "function"
    signature: str = ""
    docstring: str = ""
    java_preview: str = ""
    python_preview: str = ""
    rank: int = 0


def test_code_tokenization_and_lexical_overlap_understand_identifiers():
    assert {"fraud", "detector"} <= set(code_tokens("FraudDetector fraud_detector"))
    assert lexical_overlap("validate kyc account", "def validate_kyc_account(): pass") > 0.9


def test_hybrid_rerank_can_promote_exact_symbol_match():
    semantic = Result(0.90, "other", "other.py", "unrelated implementation")
    lexical = Result(0.70, "validate_kyc_account", "kyc.py", "def validate_kyc_account(): pass")
    ranked = hybrid_rerank("validate kyc account", [semantic, lexical], 0.5, 0.5)
    assert ranked[0].name == "validate_kyc_account"
    assert ranked[0].retrieval_method == "dense+lexical"


def test_rag_abstains_for_weak_or_ambiguous_evidence():
    weak = [Result(0.1, "weak", "weak.py", "pass")]
    assert decide_rag(weak, 0.3, 0.01, False).reason == "top_score_below_threshold"
    tied = [
        Result(0.8, "one", "one.py", "pass"),
        Result(0.795, "two", "two.py", "pass"),
    ]
    assert decide_rag(tied, 0.3, 0.01, False).reason == "ambiguous_top_results"
