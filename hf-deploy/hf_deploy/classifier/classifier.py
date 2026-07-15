"""Intent classifier: rule fast-path + embedding prototypes."""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any

from hf_deploy import CLARIFY_INTENT, INTENTS

# Prototype phrases for embedding similarity (paraphrases welcome).
PROTOTYPES: dict[str, list[str]] = {
    "text2sql": [
        "write a sql query",
        "generate a sql query",
        "translate the question into sql",
        "convert natural language to sql",
        "create a select statement",
        "query the database with sql",
    ],
    "sql2nosql": [
        "convert sql to mongodb",
        "convert sql query to nosql",
        "translate sql into mongo aggregation",
        "rewrite this sql as mongodb",
        "sql to nosql conversion",
        "generate a mongo query from sql",
        "generate nosql query for the following sql",
        "generate a mongodb query for this sql",
        "turn this sql into a nosql query",
        "convert the sql query into a mongodb shell query",
    ],
    "nosql2doc": [
        "generate documentation",
        "document this mongodb query",
        "write documentation for the collection",
        "explain this nosql query",
        "create docs for the aggregation",
        "document the mongo pipeline",
        "generate concise human-readable documentation for the mongodb query",
    ],
}

# Explicit training-style tag: "Task: text2sql" (optional but accepted).
_TASK_TAG = re.compile(
    r"(?i)^\s*task:\s*(text2sql|sql2nosql|nosql2doc)\b"
)

# Order matters: more specific intents before broader SQL phrasing.
_RULES: list[tuple[str, re.Pattern[str]]] = [
    (
        "sql2nosql",
        re.compile(
            r"(?is)\b("
            r"sql\s*to\s*(mongo|nosql)|"
            r"convert.*sql.*(mongo|nosql)|"
            r"convert.*sql.*into\s+a?\s*mongo|"
            r"mongo(db)?\s*aggregat|"
            r"rewrite.*sql.*(mongo|nosql)|"
            r"generate\s+(a\s+)?(mongo(db)?|nosql)\s+quer(?:y|ies)\b.*\bsql\b|"
            r"generate\s+(a\s+)?(mongo(db)?|nosql)\s+quer(?:y|ies)\s+"
            r"(from|for|based\s+on)\b|"
            r"turn\s+(this\s+)?sql\s+into\s+(a\s+)?(mongo|nosql)|"
            r"mongodb\s+shell\s+quer"
            r")",
        ),
    ),
    (
        "nosql2doc",
        re.compile(
            r"(?i)\b("
            r"document(ation|ing)?|"
            r"write\s+docs?|"
            r"explain\s+(this\s+)?(mongo|nosql|aggregat|collection)|"
            r"describe\s+(the\s+)?(query|pipeline|collection)|"
            r"human[- ]readable\s+documentation|"
            r"documentation\s+(for|of)\s+(this\s+)?(mongo|nosql|query|pipeline)"
            r")\b",
        ),
    ),
    (
        "text2sql",
        re.compile(
            r"(?i)\b("
            r"sql\s+query|"
            r"write\s+(a\s+)?sql|"
            r"generate\s+(a\s+)?sql|"
            r"select\s+statement|"
            r"natural\s+language\s+to\s+sql|"
            r"translate.*into\s+sql|"
            r"query\s+the\s+database|"
            r"question\s+into\s+sql"
            r")\b",
        ),
    ),
]


@dataclass(frozen=True)
class ClassificationResult:
    intent: str
    confidence: float
    method: str
    scores: dict[str, float]

    def to_dict(self) -> dict[str, Any]:
        return {
            "intent": self.intent,
            "confidence": round(self.confidence, 4),
            "method": self.method,
            "scores": {k: round(v, 4) for k, v in self.scores.items()},
        }


class IntentClassifier:
    """Classify a free-form user prompt into one LoRA task intent."""

    def __init__(
        self,
        *,
        confidence_threshold: float = 0.45,
        prefer_rules: bool = True,
        embedding_model_name: str = "sentence-transformers/all-MiniLM-L6-v2",
        use_embeddings: bool = True,
    ) -> None:
        self.confidence_threshold = confidence_threshold
        self.prefer_rules = prefer_rules
        self.embedding_model_name = embedding_model_name
        self.use_embeddings = use_embeddings
        self._embedder: Any = None
        self._prototype_vectors: dict[str, Any] | None = None

    def _ensure_embeddings(self) -> None:
        if not self.use_embeddings or self._embedder is not None:
            return
        from sentence_transformers import SentenceTransformer
        import numpy as np

        self._embedder = SentenceTransformer(self.embedding_model_name)
        self._prototype_vectors = {}
        for intent, phrases in PROTOTYPES.items():
            vectors = self._embedder.encode(phrases, normalize_embeddings=True)
            self._prototype_vectors[intent] = np.asarray(vectors, dtype=float)

    @staticmethod
    def _result(intent: str, *, confidence: float, method: str) -> ClassificationResult:
        scores = {name: 0.0 for name in INTENTS}
        if intent in scores:
            scores[intent] = confidence
        return ClassificationResult(
            intent=intent,
            confidence=confidence,
            method=method,
            scores=scores,
        )

    @classmethod
    def classify_task_tag(cls, text: str) -> ClassificationResult | None:
        """Honor an explicit ``Task: <intent>`` prefix when present."""
        match = _TASK_TAG.match(text or "")
        if match is None:
            return None
        return cls._result(match.group(1).lower(), confidence=1.0, method="task_tag")

    @classmethod
    def classify_rules(cls, text: str) -> ClassificationResult | None:
        """Return a rule match or None when no pattern fires."""
        tagged = cls.classify_task_tag(text)
        if tagged is not None:
            return tagged

        for intent, pattern in _RULES:
            if pattern.search(text):
                return cls._result(intent, confidence=0.99, method="rules")
        return None

    def classify_embeddings(self, text: str) -> ClassificationResult:
        """Score the prompt against prototype phrase embeddings."""
        import numpy as np

        self._ensure_embeddings()
        assert self._embedder is not None
        assert self._prototype_vectors is not None

        query = self._embedder.encode([text], normalize_embeddings=True)[0]
        scores: dict[str, float] = {}
        for intent in INTENTS:
            prototypes = self._prototype_vectors[intent]
            sims = prototypes @ query
            scores[intent] = float(np.max(sims))

        best_intent = max(scores, key=scores.get)
        return ClassificationResult(
            intent=best_intent,
            confidence=scores[best_intent],
            method="embedding",
            scores=scores,
        )

    def classify(self, text: str) -> ClassificationResult:
        """Classify intent; return ``clarify`` when confidence is too low."""
        cleaned = (text or "").strip()
        if not cleaned:
            return ClassificationResult(
                intent=CLARIFY_INTENT,
                confidence=0.0,
                method="empty",
                scores={name: 0.0 for name in INTENTS},
            )

        if self.prefer_rules:
            ruled = self.classify_rules(cleaned)
            if ruled is not None:
                return ruled

        if self.use_embeddings:
            result = self.classify_embeddings(cleaned)
        else:
            ruled = self.classify_rules(cleaned)
            if ruled is not None:
                return ruled
            return ClassificationResult(
                intent=CLARIFY_INTENT,
                confidence=0.0,
                method="rules_miss",
                scores={name: 0.0 for name in INTENTS},
            )

        if result.confidence < self.confidence_threshold:
            return ClassificationResult(
                intent=CLARIFY_INTENT,
                confidence=result.confidence,
                method=result.method,
                scores=result.scores,
            )
        return result
