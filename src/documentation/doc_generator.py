"""MongoDB query documentation generation using a HuggingFace model."""

from __future__ import annotations

import re
from typing import Any

from src.documentation.evaluator import DocumentationEvaluator
from src.documentation.prompt_builder import DocumentationPromptBuilder
from src.documentation.reference_builder import ReferenceDocumentationBuilder
from src.models.model_loader import CodeGenModel, is_seq2seq_model, load_model
from src.utils.schema_conversion import derive_mongo_schema_json

_CODE_FENCE_RE = re.compile(
    r"```(?:markdown|text|md)?\s*(.*?)```",
    re.DOTALL | re.IGNORECASE,
)
_MONGO_QUERY_RE = re.compile(
    r"db\.\w+\.(?:find|aggregate|distinct|countDocuments)\s*\(",
    re.IGNORECASE,
)


class DocumentationGenerator:
    """Generate plain-English documentation for MongoDB shell queries."""

    _NON_DOC_MARKER_RE = re.compile(
        r"\n(?:MongoDB query:|MongoDB:|SQL:|Python:|JavaScript:|import\s+|#include\b|\"\"\"|```)",
        re.IGNORECASE,
    )
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

    def _trim_non_doc_suffix(self, text: str) -> str:
        match = self._NON_DOC_MARKER_RE.search(text)
        if match:
            text = text[: match.start()]
        return text.strip()

    def _extract_documentation(self, raw_output: str) -> str:
        """Extract documentation text from model output."""
        text = self._trim_non_doc_suffix(raw_output.strip())

        code_match = _CODE_FENCE_RE.search(text)
        if code_match:
            candidate = code_match.group(1).strip()
            if not _MONGO_QUERY_RE.search(candidate):
                return candidate

        lines: list[str] = []
        for line in text.splitlines():
            stripped = line.strip()
            if not stripped:
                if lines:
                    break
                continue
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
            if stripped:
                lines.append(stripped)

        return " ".join(lines).strip()

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
    ) -> str:
        """Build the documentation prompt for a MongoDB query."""
        return self.prompt_builder.build(
            mongodb_query,
            schema,
            nosql_schema=nosql_schema,
        )

    def generate(
        self,
        mongodb_query: str,
        schema: str = "",
        decoding_strategy: str | None = None,
        nosql_schema: str | None = None,
    ) -> dict[str, str]:
        """Generate documentation for a single MongoDB query."""
        if nosql_schema is None and schema.strip():
            nosql_schema = derive_mongo_schema_json(schema)
        prompt = self.build_prompt(mongodb_query, schema, nosql_schema=nosql_schema)
        strategy = self._resolve_decoding_strategy(decoding_strategy)
        generate_kwargs: dict[str, Any] = {
            "max_new_tokens": self.gen_config.get("max_new_tokens", 256),
            "temperature": self.gen_config.get("temperature", 0.2),
            "top_p": self.gen_config.get("top_p", 0.95),
            "num_beams": self.gen_config.get("num_beams", 4),
            "do_sample": self.gen_config.get("do_sample", False),
            "decoding_strategy": strategy,
        }
        if not self._seq2seq:
            generate_kwargs["stop_strings"] = self._DOC_STOP_STRINGS

        model_output = self.model.generate(prompt, **generate_kwargs)
        documentation = self._extract_documentation(model_output)
        reference_documentation = self.reference_builder.build(mongodb_query)
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
