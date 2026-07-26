"""FR-1 intent detection — keyword rules first, Ollama fallback."""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Literal

from agent.clients.orchestrator_llm import OrchestratorLLM
from agent.config.settings import AgentSettings, get_settings

AgentIntent = Literal[
    "text2sql",
    "sql2nosql",
    "nosql2doc",
    "explain_sql",
    "validate_sql",
]

VALID_INTENTS: frozenset[str] = frozenset(
    {"text2sql", "sql2nosql", "nosql2doc", "explain_sql", "validate_sql"}
)

_TASK_TAG_RE = re.compile(
    r"^\s*intent\s*:\s*(text2sql|sql2nosql|nosql2doc|explain_sql|validate_sql)\b",
    re.IGNORECASE,
)
_SQL_FENCE_RE = re.compile(r"```(?:sql)?\s*(.*?)```", re.IGNORECASE | re.DOTALL)
_SELECT_RE = re.compile(r"^\s*(WITH\b|SELECT\b)", re.IGNORECASE | re.DOTALL)
_MONGO_RE = re.compile(
    r"db\.\w+\.(?:find|aggregate|distinct|countDocuments)\s*\(",
    re.IGNORECASE,
)

_RULES: list[tuple[AgentIntent, re.Pattern[str]]] = [
    (
        "validate_sql",
        re.compile(
            r"\b(validate|check|verify|is\s+this\s+sql\s+(valid|correct|safe))\b",
            re.I,
        ),
    ),
    (
        "explain_sql",
        re.compile(
            r"\b(explain\s+(this\s+)?sql|what\s+does\s+(this\s+)?sql|"
            r"explain\s+(the\s+)?query|describe\s+(this\s+)?select)\b",
            re.I,
        ),
    ),
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
            r"\b(sql\s*to\s*(mongo|nosql)|convert.*sql.*(mongo|nosql)\w*|"
            r"rewrite.*sql.*(mongo|nosql)\w*)\b",
            re.I,
        ),
    ),
    (
        "text2sql",
        re.compile(
            r"\b(sql\s+query|write\s+(a\s+)?sql|generate\s+(a\s+)?sql|"
            r"how\s+many|how\s+much|list\s+|show\s+|count\s+|top\s+\d+|"
            r"query\s+the\s+database)\b",
            re.I,
        ),
    ),
]


@dataclass(frozen=True)
class IntentResult:
    intent: AgentIntent
    confidence: float
    source: Literal["explicit", "rules", "heuristic", "llm"]


def extract_sql_from_message(text: str) -> str | None:
    match = _SQL_FENCE_RE.search(text)
    if match:
        candidate = match.group(1).strip()
        if _SELECT_RE.match(candidate):
            return candidate
    stripped = text.strip()
    if _SELECT_RE.match(stripped) and ";" not in stripped.split("\n")[0]:
        return stripped.split("\n")[0].strip()
    return None


def extract_mongo_from_message(text: str) -> str | None:
    match = _MONGO_RE.search(text)
    if not match:
        return None
    start = match.start()
    return text[start:].strip().split("\n")[0].strip()


def classify_by_rules(text: str) -> IntentResult | None:
    cleaned = text.strip()
    if not cleaned:
        return None

    tag = _TASK_TAG_RE.match(cleaned)
    if tag:
        intent = tag.group(1).lower()  # type: ignore[assignment]
        return IntentResult(intent=intent, confidence=1.0, source="explicit")

    if _MONGO_RE.search(cleaned) and re.search(
        r"\b(document|explain|describe|documentation)\b", cleaned, re.I
    ):
        return IntentResult(intent="nosql2doc", confidence=0.9, source="rules")

    if extract_sql_from_message(cleaned) or _SELECT_RE.match(cleaned):
        if re.search(r"\b(convert|mongo|nosql)\b", cleaned, re.I):
            return IntentResult(intent="sql2nosql", confidence=0.9, source="rules")
        if re.search(r"\b(explain|describe|what\s+does)\b", cleaned, re.I):
            return IntentResult(intent="explain_sql", confidence=0.9, source="rules")
        if re.search(r"\b(validate|check|verify)\b", cleaned, re.I):
            return IntentResult(intent="validate_sql", confidence=0.9, source="rules")

    for intent, pattern in _RULES:
        if pattern.search(cleaned):
            return IntentResult(intent=intent, confidence=0.85, source="rules")

    return None


def classify_by_heuristic(text: str) -> IntentResult | None:
    if extract_mongo_from_message(text):
        return IntentResult(intent="nosql2doc", confidence=0.6, source="heuristic")
    if extract_sql_from_message(text):
        return IntentResult(intent="sql2nosql", confidence=0.55, source="heuristic")
    if "?" in text or re.search(r"\b(how|what|which|who|when|where|list|show)\b", text, re.I):
        return IntentResult(intent="text2sql", confidence=0.55, source="heuristic")
    return None


class IntentDetector:
    """Detect which agent path to run for a user message."""

    def __init__(
        self,
        settings: AgentSettings | None = None,
        llm: OrchestratorLLM | None = None,
        *,
        use_llm_fallback: bool = True,
    ) -> None:
        self._settings = settings or get_settings()
        self._llm = llm or OrchestratorLLM(self._settings)
        self._use_llm_fallback = use_llm_fallback

    def detect(
        self,
        user_message: str,
        *,
        explicit_intent: str | None = None,
    ) -> IntentResult:
        if explicit_intent:
            normalized = explicit_intent.strip().lower()
            if normalized not in VALID_INTENTS:
                raise ValueError(f"Unknown intent: {explicit_intent!r}")
            return IntentResult(
                intent=normalized,  # type: ignore[arg-type]
                confidence=1.0,
                source="explicit",
            )

        ruled = classify_by_rules(user_message)
        if ruled is not None:
            return ruled

        heuristic = classify_by_heuristic(user_message)
        if heuristic is not None and heuristic.confidence >= 0.55:
            return heuristic

        if not self._use_llm_fallback:
            return IntentResult(intent="text2sql", confidence=0.4, source="heuristic")

        try:
            intent_raw, confidence = self._llm.classify_intent(user_message)
            if intent_raw in VALID_INTENTS:
                return IntentResult(
                    intent=intent_raw,  # type: ignore[arg-type]
                    confidence=confidence,
                    source="llm",
                )
        except (RuntimeError, ValueError):
            pass

        return IntentResult(intent="text2sql", confidence=0.4, source="heuristic")


def detect_intent(
    user_message: str,
    *,
    explicit_intent: str | None = None,
    settings: AgentSettings | None = None,
) -> IntentResult:
    return IntentDetector(settings=settings).detect(
        user_message,
        explicit_intent=explicit_intent,
    )
