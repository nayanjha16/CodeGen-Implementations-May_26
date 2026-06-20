"""MongoDB query generation using a HuggingFace model."""

from __future__ import annotations

import re
from typing import Any

from src.models.model_loader import CodeGenModel, is_seq2seq_model, load_model
from src.sql2nosql.evaluator import NoSQLEvaluator
from src.sql2nosql.prompt_builder import NoSQLPromptBuilder

_MONGO_START_RE = re.compile(
    r"db\.\w+\.(?:find|aggregate|distinct)\s*\(",
    re.IGNORECASE,
)
_CODE_FENCE_RE = re.compile(
    r"```(?:javascript|mongo|mongodb|js)?\s*(.*?)```",
    re.DOTALL | re.IGNORECASE,
)
_CHAIN_RE = re.compile(
    r"(\s*\.(?:sort|limit|skip|hint)\([^)]*\))+",
    re.IGNORECASE,
)


class NoSQLGenerator:
    """Generate MongoDB shell queries from natural language using a HuggingFace model."""

    _NON_MONGO_MARKER_RE = re.compile(
        r"\n(?:Output:|SQL:|import\s+|#include\b|\"\"\"|\nMongoDB:|\nMongoDB:\n)",
        re.IGNORECASE,
    )
    _MONGO_STOP_STRINGS = [
        "\nOutput:",
        "\nSQL:",
        "\nimport ",
        "\n#include",
        '\n"""',
        "\n\nMongoDB:",
        "\nMongoDB:\n",
    ]

    def __init__(
        self,
        model: CodeGenModel | None = None,
        prompt_builder: NoSQLPromptBuilder | None = None,
        config: dict[str, Any] | None = None,
    ):
        self.config = config or {}
        gen_cfg = self.config.get("generation", {})

        self.model = model or load_model(config=self.config)
        if prompt_builder is not None:
            self.prompt_builder = prompt_builder
        else:
            self.prompt_builder = NoSQLPromptBuilder.for_model(
                self.model.model_name, self.config
            )
        self.gen_config = gen_cfg
        self.evaluator = NoSQLEvaluator()
        self._seq2seq = is_seq2seq_model(self.model.model_name)

    def _trim_non_mongo_suffix(self, text: str) -> str:
        match = self._NON_MONGO_MARKER_RE.search(text)
        if match:
            text = text[: match.start()]
        return text.strip()

    def _extract_balanced_call(self, text: str) -> str:
        depth = 0
        started = False
        for index, char in enumerate(text):
            if char == "(":
                depth += 1
                started = True
            elif char == ")":
                depth -= 1
                if started and depth == 0:
                    end = index + 1
                    chain = _CHAIN_RE.match(text[end:])
                    if chain:
                        end += chain.end()
                    return text[:end].strip()
        return text.strip()

    def _extract_mongodb_query(self, raw_output: str) -> str:
        """Extract a MongoDB shell query from model output."""
        text = self._trim_non_mongo_suffix(raw_output.strip())

        code_match = _CODE_FENCE_RE.search(text)
        if code_match:
            candidate = code_match.group(1).strip()
            match = _MONGO_START_RE.search(candidate)
            if match:
                return self._extract_balanced_call(candidate[match.start() :])

        match = _MONGO_START_RE.search(text)
        if not match:
            return ""

        return self._extract_balanced_call(text[match.start() :])

    def _resolve_decoding_strategy(self, decoding_strategy: str | None) -> str:
        configured = (
            decoding_strategy or self.gen_config.get("decoding_strategy", "greedy")
        )
        if self._seq2seq and configured == "greedy":
            return self.gen_config.get("seq2seq_decoding_strategy", "beam")
        return configured

    @staticmethod
    def _parse_collection(query: str) -> str:
        match = re.match(r"db\.(\w+)\.", query.strip(), re.IGNORECASE)
        return match.group(1) if match else ""

    def is_valid_mongodb_query(self, query: str) -> bool:
        """Return True when output looks like valid MongoDB shell syntax."""
        return self.evaluator.validate_syntax(query)["valid"]

    def generate(
        self,
        question: str,
        schema: str,
        decoding_strategy: str | None = None,
    ) -> dict[str, str]:
        """Generate a MongoDB query for a single question."""
        prompt = self.prompt_builder.build(question, schema)
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
            generate_kwargs["stop_strings"] = self._MONGO_STOP_STRINGS

        raw = self.model.generate(prompt, **generate_kwargs)
        mongodb_query = self._extract_mongodb_query(raw)
        return {
            "prompt": prompt,
            "raw_output": raw,
            "mongodb_query": mongodb_query,
        }

    def generate_batch(
        self,
        examples: list[dict[str, str]],
        decoding_strategy: str | None = None,
    ) -> list[dict[str, str]]:
        """Generate MongoDB queries for multiple examples."""
        results = []
        for example in examples:
            result = self.generate(
                example["question"],
                example.get("schema", ""),
                decoding_strategy=decoding_strategy,
            )
            result["question"] = example["question"]
            result["ground_truth"] = example.get("sql", "")
            result["mongodb_valid"] = self.is_valid_mongodb_query(
                result["mongodb_query"]
            )
            results.append(result)
        return results
