"""Generate MongoDB query documentation for TEND using Qwen."""

from __future__ import annotations

from src.documentation.doc_generator import (
    DOC_MAX_NEW_TOKENS,
    build_documentation_from_model_output,
)
from src.documentation.prompt_builder import DocumentationPromptBuilder
from src.documentation.reference_builder import ReferenceDocumentationBuilder
from src.evaluation.qwen_evaluator import QwenEvaluator
from src.utils.config import get_qwen_evaluator_model_name


class QwenDocumentationGenerator:
    """Generate plain-English MongoDB query documentation with Qwen."""

    def __init__(
        self,
        model_name: str | None = None,
        evaluator: QwenEvaluator | None = None,
        max_new_tokens: int = DOC_MAX_NEW_TOKENS,
    ):
        self.model_name = model_name or get_qwen_evaluator_model_name()
        self._evaluator = evaluator
        self.max_new_tokens = max_new_tokens
        self.prompt_builder = DocumentationPromptBuilder()
        self.reference_builder = ReferenceDocumentationBuilder()

    def load(self) -> None:
        """Load the shared Qwen model if not already loaded."""
        self._get_evaluator().load()

    def _get_evaluator(self) -> QwenEvaluator:
        if self._evaluator is None:
            self._evaluator = QwenEvaluator(
                model_name=self.model_name,
                max_new_tokens=self.max_new_tokens,
            )
        return self._evaluator

    def generate(
        self,
        mongodb_query: str,
        nosql_schema: str = "",
        schema: str = "",
        question: str = "",
    ) -> dict[str, str]:
        """Generate documentation for one MongoDB shell query."""
        evaluator = self._get_evaluator()
        prompt = self.prompt_builder.build(
            mongodb_query,
            schema,
            nosql_schema=nosql_schema or None,
            question=question,
        )
        messages = [{"role": "user", "content": prompt}]
        formatted = evaluator.model.tokenizer.apply_chat_template(
            messages,
            tokenize=False,
            add_generation_prompt=True,
        )
        raw_output = evaluator.model.generate(
            formatted,
            max_new_tokens=self.max_new_tokens,
            temperature=0.1,
            do_sample=False,
            decoding_strategy="greedy",
        )
        reference_documentation = self.reference_builder.build(mongodb_query)
        documentation = build_documentation_from_model_output(
            raw_output,
            reference=reference_documentation,
        )
        return {
            "prompt": prompt,
            "raw_output": raw_output,
            "documentation": documentation,
            "reference_documentation": reference_documentation,
            "mongodb_query": mongodb_query,
            "nosql_schema": nosql_schema,
        }
