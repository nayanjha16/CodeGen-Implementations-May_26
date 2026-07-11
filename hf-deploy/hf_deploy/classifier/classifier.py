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
    ],
    "nosql2doc": [
        "generate documentation",
        "document this mongodb query",
        "write documentation for the collection",
        "explain this nosql query",
        "create docs for the aggregation",
        "document the mongo pipeline",
    ],
}

_RULES: list[tuple[str, re.Pattern[str]]] = [
    (
        "sql2nosql",
        re.compile(
            r"\b(sql\s*to\s*(mongo|nosql)|convert.*sql.*(mongo|nosql)|"
            r"mongo(db)?\s*aggregat|rewrite.*sql.*(mongo|nosql))\b",
            re.I,
        ),
    ),
    (
        "nosql2doc",
        re.compile(
            r"\b(document(ation|ing)?|write\s+docs?|explain\s+(this\s+)?"
            r"(mongo|nosql|aggregat|collection)|describe\s+(the\s+)?"
            r"(query|pipeline|collection))\b",
            re.I,
        ),
    ),
    (
        "text2sql",
        re.compile(
            r"\b(sql\s+query|write\s+(a\s+)?sql|generate\s+(a\s+)?sql|"
            r"select\s+statement|natural\s+language\s+to\s+sql|"
            r"translate.*into\s+sql|query\s+the\s+database)\b",
            re.I,
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
    def classify_rules(text: str) -> ClassificationResult | None:
        """Return a rule match or None when no pattern fires."""
        for intent, pattern in _RULES:
            if pattern.search(text):
                scores = {name: 0.0 for name in INTENTS}
                scores[intent] = 0.99
                return ClassificationResult(
                    intent=intent,
                    confidence=0.99,
                    method="rules",
                    scores=scores,
                )
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
