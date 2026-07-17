"""Prompt-based relevant table selection via embedding similarity."""

from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
from typing import Any

import numpy as np

from tool.core.activity_logger import ActivityLogger
from tool.core.schema_loader import TableSchema


@dataclass
class SchemaSelectionResult:
    selected: list[TableSchema]
    scores: dict[str, float]
    method: str
    fk_expanded: list[str]


@lru_cache(maxsize=2)
def _load_sentence_model(model_name: str) -> Any:
    from sentence_transformers import SentenceTransformer

    return SentenceTransformer(model_name)


def _cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
    norm_a = np.linalg.norm(a)
    norm_b = np.linalg.norm(b)
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return float(np.dot(a, b) / (norm_a * norm_b))


def _embed_texts(model_name: str, texts: list[str]) -> np.ndarray:
    model = _load_sentence_model(model_name)
    return model.encode(texts, normalize_embeddings=True, show_progress_bar=False)


def _question_column_boost(question: str, table: TableSchema) -> float:
    """Boost tables whose columns are mentioned in the question."""
    q = question.lower()
    boost = 0.0
    for col in table.columns:
        col_lower = col.lower()
        col_spaced = col_lower.replace("_", " ")
        if col_lower in q or col_spaced in q:
            boost += 0.12
    return min(boost, 0.36)


def _question_table_boost(question: str, table: TableSchema) -> float:
    """Boost tables whose names appear in the question."""
    q = question.lower()
    name = table.name.lower()
    spaced = name.replace("_", " ")
    boost = 0.0
    if name in q or spaced in q:
        boost += 0.1
    if name.endswith("s") and name[:-1] in q:
        boost += 0.08
    elif f"{name}s" in q or f"{spaced}s" in q:
        boost += 0.08
    return min(boost, 0.24)


def _apply_question_boosts(question: str, scored: list[tuple[TableSchema, float]]) -> list[tuple[TableSchema, float]]:
    boosted: list[tuple[TableSchema, float]] = []
    for table, score in scored:
        score += _question_column_boost(question, table)
        score += _question_table_boost(question, table)
        boosted.append((table, score))
    boosted.sort(key=lambda x: x[1], reverse=True)
    return boosted


def _tables_referenced_by_question(question: str, tables: list[TableSchema]) -> set[str]:
    """Return table names whose name or columns appear in the question."""
    q = question.lower()
    referenced: set[str] = set()
    for table in tables:
        name = table.name.lower()
        spaced = name.replace("_", " ")
        if (
            name in q
            or spaced in q
            or (name.endswith("s") and name[:-1] in q)
            or f"{name}s" in q
            or f"{spaced}s" in q
        ):
            referenced.add(table.name)
        for col in table.columns:
            col_lower = col.lower()
            col_spaced = col_lower.replace("_", " ")
            if col_lower in q or col_spaced in q:
                referenced.add(table.name)
                break
    return referenced


def _needs_fk_expansion(
    question: str,
    selected_map: dict[str, TableSchema],
    all_tables: list[TableSchema],
) -> bool:
    """Expand FK closure only when the question spans multiple tables."""
    if len(selected_map) >= 2:
        return True
    referenced = _tables_referenced_by_question(question, all_tables)
    return len(referenced) >= 2


def _expand_fk_closure(
    question: str,
    selected_map: dict[str, TableSchema],
    all_tables: list[TableSchema],
    *,
    max_tables: int,
) -> tuple[list[str], list[str]]:
    """Add direct FK parents and bridge tables needed to join selected tables."""
    if not _needs_fk_expansion(question, selected_map, all_tables):
        return [], []
    table_by_name = {t.name: t for t in all_tables}
    fk_expanded: list[str] = []
    fk_skipped: list[str] = []

    def _table_priority(table: TableSchema) -> float:
        return _question_column_boost(question, table) + _question_table_boost(question, table)

    def _add_table(name: str) -> bool:
        if name in selected_map:
            return False
        if len(selected_map) >= max_tables:
            if name not in fk_skipped:
                fk_skipped.append(name)
            return False
        ref_table = table_by_name.get(name)
        if ref_table is None:
            return False
        selected_map[name] = ref_table
        fk_expanded.append(name)
        return True

    def _add_fk_parents() -> bool:
        candidates: list[TableSchema] = []
        seen: set[str] = set()
        for table in list(selected_map.values()):
            for fk in table.foreign_keys:
                ref_table = table_by_name.get(fk["referred_table"])
                if ref_table is None or ref_table.name in selected_map or ref_table.name in seen:
                    continue
                seen.add(ref_table.name)
                candidates.append(ref_table)
        candidates.sort(key=_table_priority, reverse=True)
        return any(_add_table(table.name) for table in candidates)

    def _add_bridge_tables() -> bool:
        candidates: list[TableSchema] = []
        for table in list(selected_map.values()):
            for other in all_tables:
                if other.name in selected_map or len(other.foreign_keys) > 2:
                    continue
                if any(fk["referred_table"] == table.name for fk in other.foreign_keys):
                    candidates.append(other)
        candidates.sort(key=_table_priority, reverse=True)
        return any(_add_table(table.name) for table in candidates)

    changed = True
    while changed and len(selected_map) < max_tables:
        changed = _add_fk_parents() or _add_bridge_tables()

    return fk_expanded, fk_skipped


def _prompt_table_cap(top_k: int) -> int:
    """Allow a few join partners beyond embedding top-K."""
    return max(top_k + 3, 4)


def select_tables_for_prompt(
    question: str,
    tables: list[TableSchema],
    *,
    embedding_model: str = "BAAI/bge-small-en-v1.5",
    top_k: int = 8,
    min_score: float = 0.3,
    max_tables: int | None = None,
    logger: ActivityLogger | None = None,
) -> SchemaSelectionResult:
    """Select relevant tables for the user question."""
    prompt_cap = max_tables or _prompt_table_cap(top_k)
    if not tables:
        return SchemaSelectionResult(selected=[], scores={}, method="empty", fk_expanded=[])

    if len(tables) <= top_k:
        names = [t.name for t in tables]
        if logger:
            logger.info(
                stage="schema",
                event="tables_selected",
                message="Selected all tables (schema smaller than top-K)",
                details={"method": "full_schema", "selected": names, "total_tables": len(tables), "top_k": top_k},
            )
        return SchemaSelectionResult(selected=list(tables), scores={t.name: 1.0 for t in tables}, method="full_schema", fk_expanded=[])

    if logger:
        logger.info(stage="schema", event="schema_selection_start", message="Selecting relevant tables for prompt")

    table_texts = [t.embedding_text() for t in tables]
    try:
        table_embeddings = _embed_texts(embedding_model, table_texts)
        query_embedding = _embed_texts(embedding_model, [question.strip()])[0]
        if logger:
            logger.info(
                stage="schema",
                event="embedding_model_loaded",
                message="Embedding model ready for schema selection",
                details={"model": embedding_model},
            )
    except Exception as exc:
        boosted = _apply_question_boosts(question, [(t, 0.0) for t in tables])
        fallback_selected = [t for t, _ in boosted[:top_k]]
        names = [t.name for t in fallback_selected]
        if logger:
            logger.warning(
                stage="schema",
                event="tables_selected",
                message="Embedding failed; using question-aware fallback selection",
                details={"method": "fallback", "error": str(exc), "selected": names},
            )
        return _finalize_selection(
            question,
            tables,
            fallback_selected,
            {t.name: 0.0 for t in fallback_selected},
            method="fallback",
            top_k=top_k,
            prompt_cap=prompt_cap,
            logger=logger,
        )

    scored: list[tuple[TableSchema, float]] = []
    for idx, table in enumerate(tables):
        score = _cosine_similarity(query_embedding, table_embeddings[idx])
        if score >= min_score:
            scored.append((table, score))

    scored.sort(key=lambda x: x[1], reverse=True)
    scored = _apply_question_boosts(question, scored)
    top = scored[:top_k] if scored else sorted(
        _apply_question_boosts(
            question,
            [(tables[i], _cosine_similarity(query_embedding, table_embeddings[i])) for i in range(len(tables))],
        ),
        key=lambda x: x[1],
        reverse=True,
    )[:top_k]

    selected_map = {t.name: t for t, _ in top}
    scores = {name: score for name, score in ((t.name, s) for t, s in top)}

    return _finalize_selection(
        question,
        tables,
        list(selected_map.values()),
        scores,
        method="embedding",
        top_k=top_k,
        prompt_cap=prompt_cap,
        logger=logger,
    )


def _finalize_selection(
    question: str,
    tables: list[TableSchema],
    selected: list[TableSchema],
    scores: dict[str, float],
    *,
    method: str,
    top_k: int,
    prompt_cap: int,
    logger: ActivityLogger | None,
) -> SchemaSelectionResult:
    selected_map = {t.name: t for t in selected}
    fk_expanded, fk_skipped = _expand_fk_closure(question, selected_map, tables, max_tables=prompt_cap)
    for name in fk_expanded:
        scores[name] = 0.0

    if fk_expanded and logger:
        logger.info(
            stage="schema",
            event="fk_tables_expanded",
            message="Added FK-referenced tables to selection",
            details={"added": fk_expanded, "top_k": top_k, "max_tables": prompt_cap},
        )
    if fk_skipped and logger:
        logger.info(
            stage="schema",
            event="fk_tables_skipped",
            message="Skipped FK-referenced tables because prompt table limit was reached",
            details={"skipped": fk_skipped, "top_k": top_k, "max_tables": prompt_cap},
        )

    final_selected = list(selected_map.values())
    if logger:
        logger.info(
            stage="schema",
            event="tables_selected",
            message="Selected relevant tables for prompt",
            details={
                "method": method,
                "selected": [t.name for t in final_selected],
                "scores": {k: round(v, 3) for k, v in scores.items()},
                "top_k": top_k,
                "selected_count": len(final_selected),
                "total_tables": len(tables),
                "fk_expanded": fk_expanded,
            },
        )

    return SchemaSelectionResult(
        selected=final_selected,
        scores=scores,
        method=method,
        fk_expanded=fk_expanded,
    )


def _build_relationships_summary(tables: list[TableSchema]) -> str:
    """Summarize FK links between selected tables for join planning."""
    selected_names = {t.name for t in tables}
    lines: list[str] = []
    for table in tables:
        for fk in table.foreign_keys:
            ref_table = fk["referred_table"]
            if ref_table not in selected_names:
                continue
            lines.append(
                f"- {table.name}.{fk['column']} -> {ref_table}.{fk['referred_column']}"
            )
    if not lines:
        return ""
    return "Relationships:\n" + "\n".join(sorted(set(lines)))


def build_schema_ddl(tables: list[TableSchema]) -> str:
    """Concatenate DDL snippets and cross-table FK relationships for selected tables."""
    ddl = "\n\n".join(t.ddl for t in tables)
    relationships = _build_relationships_summary(tables)
    if not relationships:
        return ddl
    return f"{ddl}\n\n{relationships}"
