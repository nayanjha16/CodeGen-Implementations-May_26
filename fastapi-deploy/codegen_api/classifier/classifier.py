"""Intent classifier: rule fast-path + optional embedding prototypes.

Routing strategy (first hit wins):
    1. ``Task: <intent>`` tag  -> exact route (training prompt format)
    2. Regex rules             -> high-confidence keyword route
    3. Embedding prototypes    -> semantic fallback (optional dependency)
    4. Otherwise               -> ``clarify``

Order of the rules matters: ``nosql2doc`` and ``sql2nosql`` are checked before
``text2sql`` because their prompts often also contain the words "sql query".
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any

from codegen_api import CLARIFY_INTENT, INTENTS

# Short seed phrases used to build semantic prototypes when embeddings are on.
PROTOTYPES: dict[str, list[str]] = {
    "text2sql": [
        "write a sql query for this question",
        "generate sql from natural language",
        "translate this question into a select statement",
    ],
    "sql2nosql": [
        "convert this sql query to mongodb",
        "rewrite the sql as a mongo aggregation pipeline",
        "translate sql into a nosql query",
    ],
    "nosql2doc": [
        "generate documentation for this mongodb query",
        "explain what this aggregation pipeline does",
        "describe this collection and its fields",
    ],
}

# ``Task: <intent>`` fast-path (matches the fine-tuning prompt prefix).
_TASK_TAG_RE = re.compile(
    r"^\s*task\s*:\s*(text2sql|sql2nosql|nosql2doc)\b",
    re.IGNORECASE,
)

# Keyword rules, evaluated in this order.
_RULES: list[tuple[str, re.Pattern[str]]] = [
    (
        "nosql2doc",
        re.compile(
            r"\b(document(ation|ing)?|write\s+docs?|"
            r"explain\s+(this\s+)?(mongo|nosql|aggregat|collection|pipeline)|"
            r"describe\s+(the\s+)?(query|pipeline|collection))\b",
            re.I,
        ),
    ),
    (
        "sql2nosql",
        re.compile(
            r"\b(sql\s*to\s*(mongo|nosql)|convert.*sql.*(mongo|nosql)|"
            r"rewrite.*sql.*(mongo|nosql)|(mongo|nosql)(db)?\s*(query|aggregat)|"
            r"mongo(db)?\s*aggregat)\b",
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


@dataclass
class ClassificationResult:
    intent: str
    confidence: float
    method: str
    scores: dict[str, float] = field(default_factory=dict)

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
        confidence_threshold: float = 0.45,
        prefer_rules: bool = True,
        embedding_model_name: str = "sentence-transformers/all-MiniLM-L6-v2",
        use_embeddings: bool = True,
    ) -> None:
        self.confidence_threshold = confidence_threshold
        self.prefer_rules = prefer_rules
        self.embedding_model_name = embedding_model_name
        self.use_embeddings = use_embeddings
        self._embedder = None
        self._prototype_vectors: dict[str, Any] = {}

    def _ensure_embeddings(self) -> None:
        if not self.use_embeddings or self._embedder is not None:
            return
        from sentence_transformers import SentenceTransformer
        import numpy as np

        self._embedder = SentenceTransformer(self.embedding_model_name)
        for intent, phrases in PROTOTYPES.items():
            vectors = self._embedder.encode(phrases, normalize_embeddings=True)
            self._prototype_vectors[intent] = np.asarray(vectors, dtype=float)

    @staticmethod
    def classify_task_tag(text: str) -> ClassificationResult | None:
        """Route on an explicit ``Task: <intent>`` prefix, if present."""
        match = _TASK_TAG_RE.match(text)
        if not match:
            return None
        intent = match.group(1).lower()
        return ClassificationResult(
            intent=intent,
            confidence=1.0,
            method="task_tag",
            scores={name: (1.0 if name == intent else 0.0) for name in INTENTS},
        )

    @staticmethod
    def classify_rules(text: str) -> ClassificationResult | None:
        """Return a rule match or None when no pattern fires."""
        for intent, pattern in _RULES:
            if pattern.search(text):
                scores = {name: (0.95 if name == intent else 0.0) for name in INTENTS}
                return ClassificationResult(
                    intent=intent,
                    confidence=0.95,
                    method="rules",
                    scores=scores,
                )
        return None

    def classify_embeddings(self, text: str) -> ClassificationResult:
        """Score the prompt against prototype phrase embeddings."""
        import numpy as np

        self._ensure_embeddings()
        query = self._embedder.encode([text], normalize_embeddings=True)
        query = np.asarray(query, dtype=float)[0]
        scores: dict[str, float] = {}
        for intent in INTENTS:
            prototypes = self._prototype_vectors[intent]
            sims = prototypes @ query
            scores[intent] = float(max(sims))
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

        tagged = self.classify_task_tag(cleaned)
        if tagged is not None:
            return tagged

        if self.prefer_rules:
            ruled = self.classify_rules(cleaned)
            if ruled is not None:
                return ruled

        if self.use_embeddings:
            try:
                result = self.classify_embeddings(cleaned)
            except ImportError:
                # sentence-transformers not installed: fall back to clarify
                # instead of crashing the request.
                return ClassificationResult(
                    intent=CLARIFY_INTENT,
                    confidence=0.0,
                    method="embeddings_unavailable",
                    scores={name: 0.0 for name in INTENTS},
                )
            if result.confidence >= self.confidence_threshold:
                return result
            result.intent = CLARIFY_INTENT
            result.method = "low_confidence"
            return result

        return ClassificationResult(
            intent=CLARIFY_INTENT,
            confidence=0.0,
            method="rules_miss",
            scores={name: 0.0 for name in INTENTS},
        )
