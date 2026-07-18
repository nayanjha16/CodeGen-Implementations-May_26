"""Documentation generation for MongoDB queries."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .doc_generator import DocumentationGenerator
    from .evaluator import DocumentationEvaluator
    from .prompt_builder import DocumentationPromptBuilder
    from .reference_builder import ReferenceDocumentationBuilder

__all__ = [
    "DocumentationGenerator",
    "DocumentationPromptBuilder",
    "DocumentationEvaluator",
    "ReferenceDocumentationBuilder",
    "build_documentation_from_model_output",
    "documentation_contains_code",
    "extract_documentation_from_output",
]


def __getattr__(name: str):
    if name == "DocumentationGenerator":
        from .doc_generator import DocumentationGenerator

        return DocumentationGenerator
    if name == "DocumentationPromptBuilder":
        from .prompt_builder import DocumentationPromptBuilder

        return DocumentationPromptBuilder
    if name == "DocumentationEvaluator":
        from .evaluator import DocumentationEvaluator

        return DocumentationEvaluator
    if name == "ReferenceDocumentationBuilder":
        from .reference_builder import ReferenceDocumentationBuilder

        return ReferenceDocumentationBuilder
    if name == "build_documentation_from_model_output":
        from .doc_generator import build_documentation_from_model_output

        return build_documentation_from_model_output
    if name == "documentation_contains_code":
        from .doc_generator import documentation_contains_code

        return documentation_contains_code
    if name == "extract_documentation_from_output":
        from .doc_generator import extract_documentation_from_output

        return extract_documentation_from_output
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
