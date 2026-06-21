"""MongoDB query documentation generation using a HuggingFace model."""

from __future__ import annotations

import re
from typing import Any

from src.documentation.evaluator import DocumentationEvaluator
from src.documentation.prompt_builder import DocumentationPromptBuilder
from src.documentation.reference_builder import ReferenceDocumentationBuilder
from src.models.model_loader import CodeGenModel, is_seq2seq_model, load_model
from src.utils.schema_conversion import derive_mongo_schema_json

DOC_MAX_NEW_TOKENS = 256
DOC_MAX_CHARS = 500
DOC_MAX_SENTENCES = 3


_MONGO_QUERY_RE = re.compile(
    r"db\.\w+\.(?:find|aggregate|distinct|countDocuments)\s*\(",
    re.IGNORECASE,
)
_NON_DOC_MARKER_RE = re.compile(
    r"\n(?:MongoDB query:|MongoDB:|SQL:|Python:|JavaScript:|import\s+|#include\b|\"\"\"|```)",
    re.IGNORECASE,
)
_HEADING_RE = re.compile(r"^#+\s*", re.MULTILINE)
_FILLER_PREFIX_RE = re.compile(
    r"^(?:"
    r"(?:query explanation|mongodb query documentation)\s*"
    r"|the mongodb (?:shell )?query (?:you(?:'ve| have) provided|below)\s*"
    r"(?:is used to |aims to )?"
    r"|here(?:'s| is) (?:a |the )?(?:breakdown|explanation)[:\s]*"
    r")+",
    re.IGNORECASE,
)
_CODE_FENCE_BLOCK_RE = re.compile(
    r"```(?:[\w+-]*)?\s*.*?```",
    re.DOTALL | re.IGNORECASE,
)
_CODE_FENCE_OPEN_RE = re.compile(
    r"```(?:[\w+-]*)?\s*.*",
    re.DOTALL | re.IGNORECASE,
)
_JSON_LIKE_RE = re.compile(
    r"\{[\s\S]*?(?:\$?(?:query|match|group|project|sort|filter|distinct)|\"[\w.]+\")[\s\S]*?\}",
    re.IGNORECASE,
)
_PIPELINE_OPERATOR_RE = re.compile(r"\$(\w+)")
_BACKTICK_RE = re.compile(r"`([^`]+)`")


def _strip_code_fences(text: str) -> str:
    """Remove fenced and trailing code blocks from model output."""
    text = _CODE_FENCE_BLOCK_RE.sub("", text)
    text = _CODE_FENCE_OPEN_RE.sub("", text)
    return text.strip()


def documentation_contains_code(text: str) -> bool:
    """Return True when documentation still contains code-like syntax."""
    text = text.strip()
    if not text:
        return False
    if _MONGO_QUERY_RE.search(text):
        return True
    if "```" in text or "`" in text:
        return True
    if _PIPELINE_OPERATOR_RE.search(text):
        return True
    if _JSON_LIKE_RE.search(text):
        return True
    if text.count("{") >= 1 and text.count(":") >= 2:
        return True
    return False


def sanitize_documentation(text: str) -> str:
    """Remove code, JSON, and operator syntax from documentation text."""
    text = text.strip()
    if not text:
        return ""

    text = _strip_code_fences(text)
    text = _JSON_LIKE_RE.sub("", text)
    text = _HEADING_RE.sub("", text)
    text = _MONGO_QUERY_RE.sub("", text)
    text = _BACKTICK_RE.sub(r"\1", text)
    text = _PIPELINE_OPERATOR_RE.sub(lambda match: match.group(1).lower(), text)
    text = re.sub(r"\s+", " ", text).strip()

    while True:
        trimmed = _FILLER_PREFIX_RE.sub("", text, count=1).strip()
        if trimmed == text:
            break
        text = trimmed

    return text.strip()


def _trim_non_doc_suffix(text: str) -> str:
    match = _NON_DOC_MARKER_RE.search(text)
    if match:
        text = text[: match.start()]
    return text.strip()


def compact_documentation(
    text: str,
    *,
    max_chars: int = DOC_MAX_CHARS,
    max_sentences: int = DOC_MAX_SENTENCES,
) -> str:
    """Trim model output to a short, commit-message-style description."""
    text = text.strip()
    if not text:
        return ""

    text = _HEADING_RE.sub("", text)
    text = re.sub(r"\s+", " ", text).strip()
    while True:
        trimmed = _FILLER_PREFIX_RE.sub("", text, count=1).strip()
        if trimmed == text:
            break
        text = trimmed

    sentences = [part.strip() for part in re.split(r"(?<=[.!?])\s+", text) if part.strip()]
    if max_sentences and len(sentences) > max_sentences:
        text = " ".join(sentences[:max_sentences])
    elif sentences:
        text = " ".join(sentences)

    if len(text) > max_chars:
        truncated = text[: max_chars - 3].rsplit(" ", 1)[0]
        text = f"{truncated}..." if truncated else text[:max_chars]

    return text.strip()


def extract_documentation_from_output(raw_output: str) -> str:
    """Extract plain-English documentation from raw model output."""
    text = _trim_non_doc_suffix(raw_output.strip())
    text = _strip_code_fences(text)

    lines: list[str] = []
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        if stripped.startswith("```") or _looks_like_code_line(stripped):
            break
        if _MONGO_QUERY_RE.search(stripped):
            break
        if stripped.lower().startswith(
            ("documentation:", "output:", "answer:", "response:")
        ):
            stripped = re.sub(
                r"^(?:documentation|output|answer|response)\s*:\s*",
                "",
                stripped,
                flags=re.IGNORECASE,
            )
        if stripped and not _looks_like_code_line(stripped):
            lines.append(stripped)

    return " ".join(lines).strip()


def _looks_like_code_line(line: str) -> bool:
    stripped = line.strip()
    if not stripped:
        return False
    if stripped.startswith(("{", "[", "}", "]", "```")):
        return True
    if _MONGO_QUERY_RE.search(stripped):
        return True
    if _JSON_LIKE_RE.search(stripped):
        return True
    if stripped.count(":") >= 2 and ('"' in stripped or "'" in stripped):
        return True
    return False


def build_documentation_from_model_output(
    raw_output: str,
    *,
    reference: str = "",
    min_chars: int = 20,
) -> str:
    """Extract, sanitize, and compact documentation with rule-based fallback."""
    candidate = compact_documentation(
        sanitize_documentation(extract_documentation_from_output(raw_output))
    )
    if (
        candidate
        and len(candidate) >= min_chars
        and not documentation_contains_code(candidate)
    ):
        return candidate

    fallback = compact_documentation(sanitize_documentation(reference))
    if fallback and not documentation_contains_code(fallback):
        return fallback
    return candidate


class DocumentationGenerator:
    """Generate plain-English documentation for MongoDB shell queries."""

    _DOC_STOP_STRINGS = [
        "\nMongoDB query:",
        "\nMongoDB:",
        "\nSQL:",
        "\nPython:",
        "\nJavaScript:",
        "\nimport ",
        "\n#include",
        '\n"""',
        "\n```",
        "\n\nMongoDB:",
    ]

    def __init__(
        self,
        model: CodeGenModel | None = None,
        prompt_builder: DocumentationPromptBuilder | None = None,
        config: dict[str, Any] | None = None,
    ):
        self.config = config or {}
        gen_cfg = self.config.get("generation", {})

        self.model = model or load_model(config=self.config)
        if prompt_builder is not None:
            self.prompt_builder = prompt_builder
        else:
            self.prompt_builder = DocumentationPromptBuilder.for_model(
                self.model.model_name, self.config
            )
        self.gen_config = gen_cfg
        self.evaluator = DocumentationEvaluator()
        self.reference_builder = ReferenceDocumentationBuilder()
        self._seq2seq = is_seq2seq_model(self.model.model_name)

    def _extract_documentation(self, raw_output: str, mongodb_query: str = "") -> str:
        """Extract documentation text from model output."""
        reference = self.reference_builder.build(mongodb_query)
        return build_documentation_from_model_output(
            raw_output,
            reference=reference,
        )

    def _resolve_decoding_strategy(self, decoding_strategy: str | None) -> str:
        configured = (
            decoding_strategy or self.gen_config.get("decoding_strategy", "greedy")
        )
        if self._seq2seq and configured == "greedy":
            return self.gen_config.get("seq2seq_decoding_strategy", "beam")
        return configured

    def is_valid_documentation(
        self,
        documentation: str,
        mongodb_query: str = "",
    ) -> bool:
        """Return True when output looks like usable documentation."""
        return self.evaluator.validate_structure(documentation, mongodb_query)["valid"]

    def build_prompt(
        self,
        mongodb_query: str,
        schema: str = "",
        nosql_schema: str | None = None,
        question: str = "",
    ) -> str:
        """Build the documentation prompt for a MongoDB query."""
        return self.prompt_builder.build(
            mongodb_query,
            schema,
            nosql_schema=nosql_schema,
            question=question,
        )

    def generate(
        self,
        mongodb_query: str,
        schema: str = "",
        decoding_strategy: str | None = None,
        nosql_schema: str | None = None,
        question: str = "",
    ) -> dict[str, str]:
        """Generate documentation for a single MongoDB query."""
        if nosql_schema is None and schema.strip():
            nosql_schema = derive_mongo_schema_json(schema)
        prompt = self.build_prompt(
            mongodb_query,
            schema,
            nosql_schema=nosql_schema,
            question=question,
        )
        strategy = self._resolve_decoding_strategy(decoding_strategy)
        generate_kwargs: dict[str, Any] = {
            "max_new_tokens": self.gen_config.get(
                "documentation_max_new_tokens", DOC_MAX_NEW_TOKENS
            ),
            "temperature": self.gen_config.get("temperature", 0.2),
            "top_p": self.gen_config.get("top_p", 0.95),
            "num_beams": self.gen_config.get("num_beams", 4),
            "do_sample": self.gen_config.get("do_sample", False),
            "decoding_strategy": strategy,
        }
        if not self._seq2seq:
            generate_kwargs["stop_strings"] = self._DOC_STOP_STRINGS

        model_output = self.model.generate(prompt, **generate_kwargs)
        reference_documentation = self.reference_builder.build(mongodb_query)
        documentation = self._extract_documentation(model_output, mongodb_query)
        return {
            "prompt": prompt,
            "raw_output": model_output,
            "documentation": documentation,
            "reference_documentation": reference_documentation,
            "mongodb_query": mongodb_query,
            "nosql_schema": nosql_schema or "",
        }

    def generate_batch(
        self,
        examples: list[dict[str, str]],
        decoding_strategy: str | None = None,
    ) -> list[dict[str, str]]:
        """Generate documentation for multiple MongoDB queries."""
        results: list[dict[str, str]] = []
        for example in examples:
            schema = example.get("schema", "")
            mongodb_query = example.get(
                "mongodb_query",
                example.get("predicted_mongodb_query", ""),
            )
            nosql_schema = example.get("nosql_schema") or (
                derive_mongo_schema_json(schema) if schema.strip() else ""
            )
            result = self.generate(
                mongodb_query,
                schema,
                decoding_strategy=decoding_strategy,
                nosql_schema=nosql_schema,
                question=example.get("question", ""),
            )
            result["question"] = example.get("question", "")
            result["schema"] = schema
            result["reference_mongodb_query"] = example.get(
                "reference_mongodb_query", ""
            )
            result["reference_sql"] = example.get("reference_sql", "")
            result["documentation_valid"] = self.is_valid_documentation(
                result["documentation"],
                mongodb_query,
            )
            results.append(result)
        return results
