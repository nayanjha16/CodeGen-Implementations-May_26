"""
Prompt construction for both model paths and all three multi-task operations.
All prompt format differences are strictly isolated here.

CodeGen uses structured multi-task system instructions with structural anchoring blocks.
CodeT5 uses compact prefix-delimited tokens to maintain semantic density.
"""

# -*- coding: utf-8 -*-

def _cap(text: str) -> str:
    """Internal helper to ensure clean syntax spacing."""
    return str(text).strip()


# ---------------------------------------------------------------------------
# Task descriptions — injected after the task tag in every CodeGen prompt.
# Natural-language format; describe inputs, enumerate query/clause types, and
# state output constraints explicitly so the 350M model can connect the parts.
# ---------------------------------------------------------------------------

_TEXT2SQL_TASK_DESC = "Translate the natural language question into a valid SQL query using the provided schema."

_SQL2NOSQL_TASK_DESC = "Translate the SQL query into an equivalent MongoDB MQL query using the provided schema."

_TEXT2NOSQL_TASK_DESC = "Translate the natural language question into a MongoDB MQL query using the provided schema."


# ---------------------------------------------------------------------------
# Task 1: Text-to-SQL (With Teacher Calibration Capacity)
# ---------------------------------------------------------------------------
def build_text2sql_sample(
    model_type: str,
    question: str,
    db_id: str,
    sql: str,
    schema_maps: dict,
    broken_draft: str = "",
    teacher_analysis: str = "",
    for_inference: bool = False,
    retrieved_example: dict = None,
    skip_rag: bool = False,  # Safety valve for 2048 budget control
    schema_pruner=None,      # SchemaPruner instance, or None to use full schema
):
    """Returns (input_text, target_text) for NL-to-SQL training/inference."""
    schema = schema_maps.get(db_id, "-- schema unavailable")
    if schema_pruner is not None and schema != "-- schema unavailable":
        schema = schema_pruner.prune_text(schema, question, db_id, dataset="spider")

    if model_type == "codegen":
        ref_part = ""
        if retrieved_example and not skip_rag:
            ex_q = retrieved_example.get("question", "")
            ex_sql = _cap(retrieved_example.get("gold_sql", retrieved_example.get("query", "")))
            ref_part = f"Reference:\nQuestion: {ex_q}\nSQL: {ex_sql}\n\n"

        draft_line = f"Draft: {broken_draft}\n\n" if broken_draft else ""
        input_text = (
            f"{_TEXT2SQL_TASK_DESC}\n\n"
            f"{ref_part}"
            f"Schema:\n{schema}\n\n"
            f"Question:\n{question}\n\n"
            f"{draft_line}"
            f"SQL:\n"
        )
        if for_inference:
            target_text = ""
        elif teacher_analysis:
            target_text = f"Analysis: {teacher_analysis} | Corrected_SQL: {sql}"
        else:
            target_text = sql

    else:  # CodeT5 path
        example_prefix = ""
        if retrieved_example and not skip_rag:
            ex_q = retrieved_example.get("question", "")
            ex_sql = _cap(retrieved_example.get("gold_sql", retrieved_example.get("query", "")))
            example_prefix = f"example: {ex_q} | {ex_sql}\n"

        input_text = f"{example_prefix}translate to sql: {question} | {schema}"
        target_text = "" if for_inference else sql

    return input_text, target_text


# ---------------------------------------------------------------------------
# Task 2: SQL-to-NoSQL (Transpilation Execution)
# ---------------------------------------------------------------------------
def build_sql2nosql_sample(
    model_type: str,
    sql: str,
    db_id: str,
    mql: str,
    schema_maps: dict,
    broken_draft: str = "",
    teacher_analysis: str = "",
    for_inference: bool = False,
    retrieved_example: dict = None,
    skip_rag: bool = False,
    schema_pruner=None,      # SchemaPruner instance, or None to use full schema
):
    """Returns (input_text, target_text) for Relational-to-Document transpilation."""
    schema = schema_maps.get(db_id, "-- schema unavailable")
    if schema_pruner is not None and schema != "-- schema unavailable":
        schema = schema_pruner.prune_sql2nosql(schema, sql)

    if model_type == "codegen":
        ref_part = ""
        if retrieved_example and not skip_rag:
            ex_sql = _cap(retrieved_example.get("spider_gold_sql", ""))
            ex_mql = _cap(retrieved_example.get("query", ""))
            ref_part = f"Reference:\nSQL: {ex_sql}\nMQL: {ex_mql}\n\n"

        draft_line = f"Draft: {broken_draft}\n\n" if broken_draft else ""
        input_text = (
            f"{_SQL2NOSQL_TASK_DESC}\n\n"
            f"{ref_part}"
            f"Schema:\n{schema}\n\n"
            f"SQL:\n{sql}\n\n"
            f"{draft_line}"
            f"MQL:\n"
        )
        if for_inference:
            target_text = ""
        elif teacher_analysis:
            target_text = f"Analysis: {teacher_analysis} | Final_MQL: {mql}"
        else:
            target_text = mql

    else:  # CodeT5 path
        example_prefix = ""
        if retrieved_example and not skip_rag:
            ex_sql = _cap(retrieved_example.get("spider_gold_sql", ""))
            ex_mql = _cap(retrieved_example.get("query", ""))
            example_prefix = f"example: {ex_sql} | {ex_mql}\n"

        input_text = f"{example_prefix}translate sql to mql: {sql} | {schema}"
        target_text = "" if for_inference else mql

    return input_text, target_text


# ---------------------------------------------------------------------------
# Task 3: Text-to-NoSQL (Direct Native Generation)
# ---------------------------------------------------------------------------
def build_text2nosql_sample(
    model_type: str,
    question: str,
    db_id: str,
    mql: str,
    schema_maps: dict,
    broken_draft: str = "",
    teacher_analysis: str = "",
    for_inference: bool = False,
    retrieved_example: dict = None,
    skip_rag: bool = False,
    schema_pruner=None,      # SchemaPruner instance, or None to use full schema
):
    """Returns (input_text, target_text) for direct Natural Language-to-MQL synthesis."""
    schema = schema_maps.get(db_id, "-- schema unavailable")
    if schema_pruner is not None and schema != "-- schema unavailable":
        schema = schema_pruner.prune_text(schema, question, db_id, dataset="docspider")

    if model_type == "codegen":
        ref_part = ""
        if retrieved_example and not skip_rag:
            ex_q = retrieved_example.get("question", "")
            ex_mql = _cap(retrieved_example.get("query", ""))
            ref_part = f"Reference:\nQuestion: {ex_q}\nMQL: {ex_mql}\n\n"

        draft_line = f"Draft: {broken_draft}\n\n" if broken_draft else ""
        input_text = (
            f"{_TEXT2NOSQL_TASK_DESC}\n\n"
            f"{ref_part}"
            f"Schema:\n{schema}\n\n"
            f"Question:\n{question}\n\n"
            f"{draft_line}"
            f"MQL:\n"
        )
        if for_inference:
            target_text = ""
        elif teacher_analysis:
            target_text = f"Analysis: {teacher_analysis} | Final_MQL: {mql}"
        else:
            target_text = mql

    else:  # CodeT5 path
        example_prefix = ""
        if retrieved_example and not skip_rag:
            ex_q = retrieved_example.get("question", "")
            ex_mql = _cap(retrieved_example.get("query", ""))
            example_prefix = f"example: {ex_q} | {ex_mql}\n"

        input_text = f"{example_prefix}translate text to mql: {question} | {schema}"
        target_text = "" if for_inference else mql

    return input_text, target_text