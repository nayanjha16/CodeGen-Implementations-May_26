"""Documentation generation evaluation module."""

from __future__ import annotations

import re
from typing import Any

from src.documentation.reference_builder import ReferenceDocumentationBuilder
from src.evaluation.embedding_similarity import embedding_similarity_batch
from src.utils.config import get_embedding_model_name


class DocumentationEvaluator:
    """Evaluate MongoDB query documentation quality."""

    def __init__(self, reference_builder: ReferenceDocumentationBuilder | None = None):
        self.reference_builder = reference_builder or ReferenceDocumentationBuilder()

    def validate_structure(
        self,
        documentation: str,
        mongodb_query: str = "",
    ) -> dict[str, Any]:
        """Check whether generated documentation looks usable."""
        text = documentation.strip()
        if len(text) < 20:
            return {"valid": False, "reason": "Documentation is too short"}

        from src.documentation.doc_generator import documentation_contains_code

        if documentation_contains_code(text):
            return {"valid": False, "reason": "Documentation contains code"}

        if re.search(r"db\.\w+\.(find|aggregate|distinct|countDocuments)\s*\(", text):
            return {"valid": False, "reason": "Documentation contains raw MongoDB code"}

        structured = self.reference_builder.to_structured(mongodb_query)
        if structured.get("valid"):
            collection = structured["collection"].lower()
            if collection and collection not in text.lower():
                return {
                    "valid": False,
                    "reason": f"Documentation does not mention collection `{structured['collection']}`",
                }

        return {"valid": True, "reason": ""}

    def evaluate_all(
        self,
        predictions: list[str],
        references: list[str],
        *,
        embedding_model: str | None = None,
    ) -> dict[str, Any]:
        """Run documentation evaluation using embedding similarity."""
        model_name = embedding_model or get_embedding_model_name()
        return {
            "embedding_similarity": embedding_similarity_batch(
                predictions,
                references,
                model_name=model_name,
            ),
        }
