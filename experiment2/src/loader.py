import json
import os
import re
import logging
from src.config import DATA
from src.logger import pipeline_logger

# Configure basic logging for the module
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

# ---------------------------------------------------------------------------
# Schema utilities
# ---------------------------------------------------------------------------

def minify_sql_schema(schema_str: str) -> str:
    """Convert verbose CREATE TABLE DDL to compact table(col1, col2) | ... format."""
    if not isinstance(schema_str, str) or not schema_str or "-- schema unavailable" in schema_str:
        return ""
    table_matches = re.findall(r'CREATE\s+TABLE\s+(\w+)\s*\((.*?)\);', schema_str, re.DOTALL | re.IGNORECASE)
    if not table_matches:
        return re.sub(r'\s+', ' ', schema_str).strip()
    tables = []
    for tname, cols_block in table_matches:
        cols = []
        for col in cols_block.split(','):
            col = col.strip()
            if not col:
                continue
            if any(k in col.upper() for k in ["FOREIGN KEY", "PRIMARY KEY", "CONSTRAINT", "REFERENCES"]):
                continue
            parts = col.split()
            if parts:
                cols.append(parts[0])
        tables.append(f"{tname}({', '.join(cols)})")
    return " | ".join(tables)


# ---------------------------------------------------------------------------
# Schema Compilers & Footprint Maps
# ---------------------------------------------------------------------------

def load_spider_schema_maps():
    """
    Reads tables.json and builds DDL CREATE TABLE blocks per database.
    Used by CodeGen prompts.
    """
    TABLES_PATH = DATA["spider_tables"]
    if not os.path.exists(TABLES_PATH):
        raise FileNotFoundError(f"Tables schema file not found at: {TABLES_PATH}")
        
    try:
        with open(TABLES_PATH, "r", encoding="utf-8") as f:
            tables_data = json.load(f)
    except json.JSONDecodeError as e:
        logging.error(f"Failed to parse JSON in {TABLES_PATH}")
        raise e
        
    schema_map = {}
    for db in tables_data:
        db_id = db["db_id"]
        table_names = db["table_names_original"]
        column_names = db["column_names_original"]
        column_types = db["column_types"]

        # Map out table indexes to empty column dictionaries
        table_columns = {i: [] for i in range(len(table_names))}

        # Zip column schemas together
        for idx, (table_idx, col_name) in enumerate(column_names):
            if table_idx != -1:  # Skip global wildcard *
                col_type = column_types[idx]
                table_columns[table_idx].append(f"    {col_name} {col_type}")

        # Build standard mock DDL strings
        ddl_tables = []
        for idx, t_name in enumerate(table_names):
            cols_str = ",\n".join(table_columns[idx])
            ddl_table = f"CREATE TABLE {t_name} (\n{cols_str}\n);"
            ddl_tables.append(ddl_table)

        schema_map[db_id] = "\n\n".join(ddl_tables)

    pipeline_logger.info("data_loading", "spider_schema_maps_loaded", stats={
        "path": TABLES_PATH,
        "db_count": len(schema_map)
    })
    return schema_map


def load_spider_compact_schema_maps():
    """
    Builds a compact pipe-delimited schema string per database.
    Format: "db_id | table1: col1, col2 | table2: col1"
    Used by CodeT5+ prompts (adopted from experiment 1 — shorter, fits encoder better).
    """
    TABLES_PATH = DATA["spider_tables"]
    if not os.path.exists(TABLES_PATH):
        raise FileNotFoundError(f"Tables schema file not found at: {TABLES_PATH}")

    with open(TABLES_PATH, "r", encoding="utf-8") as f:
        tables_data = json.load(f)

    schema_map = {}
    for db in tables_data:
        db_id        = db["db_id"]
        table_names  = db["table_names_original"]
        column_names = db["column_names_original"]

        table_columns = {i: [] for i in range(len(table_names))}
        for table_idx, col_name in column_names:
            if table_idx != -1:
                table_columns[table_idx].append(col_name)

        parts = [db_id]
        for idx, t_name in enumerate(table_names):
            cols = ", ".join(table_columns[idx])
            parts.append(f"{t_name}: {cols}")

        schema_map[db_id] = " | ".join(parts)

    return schema_map


def load_schema_context_map(collections_json_path):
    """
    Parses collections.json into a structural scannable text mapping for DocSpider:
    db_id -> "Collection1(field1, field2) | Collection2(field1)"
    """
    if not os.path.exists(collections_json_path):
        raise FileNotFoundError(f"Collections file not found at: {collections_json_path}")

    with open(collections_json_path, "r", encoding="utf-8") as f:
        schema_data = json.load(f)
        
    schema_map = {}
    for db in schema_data:
        db_id = db["db_id"]
        collections = db["collection_names"]
        columns = db["column_names"]

        grouped_collections = {i: [] for i in range(len(collections))}
        for col in columns:
            col_idx = col[0]
            col_name = col[1]
            if col_idx in grouped_collections:
                grouped_collections[col_idx].append(col_name)

        collection_strings = []
        for idx, col_name in enumerate(collections):
            fields = ", ".join(grouped_collections[idx])
            collection_strings.append(f"{col_name}({fields})")

        schema_map[db_id] = " | ".join(collection_strings)

    pipeline_logger.info("data_loading", "docspider_schema_map_loaded", stats={
        "path": collections_json_path,
        "db_count": len(schema_map)
    })
    return schema_map


def load_spider_compact_schema_maps_with_fk():
    """
    Builds compact pipe-delimited schema per database, including FK annotations.
    Format: table1(col1, col2->ref_table.ref_col, col3) | table2(col1, col2)
    FK suffix on a column shows which table/column it references, giving the model
    join-path information without the token cost of full DDL.
    """
    TABLES_PATH = DATA["spider_tables"]
    if not os.path.exists(TABLES_PATH):
        raise FileNotFoundError(f"Tables schema file not found at: {TABLES_PATH}")

    with open(TABLES_PATH, "r", encoding="utf-8") as f:
        tables_data = json.load(f)

    schema_map = {}
    for db in tables_data:
        db_id = db["db_id"]
        table_names = db["table_names_original"]
        column_names = db["column_names_original"]  # [(table_idx, col_name), ...]
        foreign_keys = db.get("foreign_keys", [])   # [[fk_col_idx, ref_col_idx], ...]

        # Build FK lookup: global col index -> "->ref_table.ref_col"
        fk_map = {}
        for fk_col_idx, ref_col_idx in foreign_keys:
            if ref_col_idx < len(column_names):
                ref_table_idx, ref_col_name = column_names[ref_col_idx]
                if ref_table_idx != -1 and ref_table_idx < len(table_names):
                    fk_map[fk_col_idx] = f"->{table_names[ref_table_idx]}.{ref_col_name}"

        # Group columns by table, appending FK annotation where applicable
        table_columns = {i: [] for i in range(len(table_names))}
        for global_idx, (table_idx, col_name) in enumerate(column_names):
            if table_idx != -1:
                fk_suffix = fk_map.get(global_idx, "")
                table_columns[table_idx].append(f"{col_name}{fk_suffix}")

        parts = []
        for idx, t_name in enumerate(table_names):
            cols = ", ".join(table_columns[idx])
            parts.append(f"{t_name}({cols})")

        schema_map[db_id] = " | ".join(parts)

    pipeline_logger.info("data_loading", "spider_schema_maps_with_fk_loaded", stats={
        "path": TABLES_PATH,
        "db_count": len(schema_map)
    })
    return schema_map


def load_spider_table_names_map():
    """Returns {db_id: [table_names_original]} for RAG retrieval queries."""
    with open(DATA["spider_tables"], "r", encoding="utf-8") as f:
        tables_data = json.load(f)
    return {db["db_id"]: db["table_names_original"] for db in tables_data}


def load_spider_fk_neighbors_map():
    """
    Returns {db_id: {table_name: [fk_connected_table_names]}} for schema
    pruning FK expansion.  Both directions of every FK are included so that
    a question mentioning only one side of a join still pulls in the other.
    """
    with open(DATA["spider_tables"], "r", encoding="utf-8") as f:
        tables_data = json.load(f)

    result = {}
    for db in tables_data:
        db_id        = db["db_id"]
        table_names  = db["table_names_original"]
        column_names = db["column_names_original"]
        foreign_keys = db.get("foreign_keys", [])

        neighbors = {t: set() for t in table_names}
        for fk_col_idx, ref_col_idx in foreign_keys:
            if fk_col_idx < len(column_names) and ref_col_idx < len(column_names):
                from_t_idx = column_names[fk_col_idx][0]
                to_t_idx   = column_names[ref_col_idx][0]
                if from_t_idx != -1 and to_t_idx != -1:
                    from_t = table_names[from_t_idx]
                    to_t   = table_names[to_t_idx]
                    neighbors[from_t].add(to_t)
                    neighbors[to_t].add(from_t)

        result[db_id] = {t: list(v) for t, v in neighbors.items()}

    return result


# ---------------------------------------------------------------------------
# Task File Readers
# ---------------------------------------------------------------------------

def load_spider_tasks(dataset_path, limit=None):
    """
    Reads a Spider JSON file (supports raw train/dev data or intermediate 
    augmented calibration dataset variants cleanly).
    """
    if not os.path.exists(dataset_path):
        raise FileNotFoundError(f"Dataset file not found at: {dataset_path}")

    with open(dataset_path, "r", encoding="utf-8") as f:
        tasks = json.load(f)

    result = tasks[:limit] if limit else tasks
    pipeline_logger.info("data_loading", "spider_tasks_loaded", stats={
        "path": dataset_path,
        "total_tasks": len(tasks),
        "returned": len(result),
        "limit_applied": limit is not None
    })
    return result

  
def load_docspider_tasks(dataset_path, limit=None):
    """
    Reads a DocSpider JSON file (train.json or dev.json).
    Skips incomplete entries missing relational or document structural components.
    """
    if not os.path.exists(dataset_path):
        raise FileNotFoundError(f"DocSpider file not found at: {dataset_path}")

    with open(dataset_path, "r", encoding="utf-8") as f:
        raw = json.load(f)

    tasks = []
    skipped = 0
    for entry in raw:
        sql = entry.get("spider_gold_sql", "").strip()
        mql = entry.get("query", "").strip()
        if sql and mql:
            tasks.append(entry)
        else:
            skipped += 1

    result = tasks[:limit] if limit else tasks
    pipeline_logger.info("data_loading", "docspider_tasks_loaded", stats={
        "path": dataset_path,
        "total_raw": len(raw),
        "valid": len(tasks),
        "skipped_incomplete": skipped,
        "returned": len(result),
        "limit_applied": limit is not None
    })
    return result


# ---------------------------------------------------------------------------
# Evaluation Framework Prompt Routines (Aligned to Unified Context Targets)
# ---------------------------------------------------------------------------

def construct_unified_eval_prompt(task, schema_map, task_type="text2sql"):
    """
    Generates exact structural contexts matching the system training architecture
    so evaluation sequences encounter identical adapter boundary triggers.
    """
    db_id = task.get("db_id", "unknown_db")
    schema = schema_map.get(db_id, "-- Schema unavailable")
    
    if schema == "-- Schema unavailable":
        logging.warning(f"Schema missing for db_id: {db_id}")
    
    if task_type == "text2sql":
        question = task.get("question", "")
        broken_draft = task.get("broken_draft", "")
        draft_line = f"Broken Draft: {broken_draft}\n" if broken_draft else ""

        return (
            f"[Task: NL-to-SQL]\n"
            f"### TARGET TASK ###\n"
            f"Question: {question}\n"
            f"Schema: {schema}\n"
            f"{draft_line}"
            f"\n### SYSTEM RESPONSE ###\n"
            f"Analysis:"
        )

    elif task_type == "sql2nosql":
        sql_query = task.get("spider_gold_sql", task.get("query", ""))
        return (
            f"[Task: SQL-to-MQL]\n"
            f"### TARGET TASK ###\n"
            f"Input SQL: {sql_query}\n"
            f"Schema: {schema}\n\n"
            f"### SYSTEM RESPONSE ###\n"
            f"Analysis:"
        )

    elif task_type == "text2nosql":
        question = task.get("question", "")
        return (
            f"[Task: NL-to-MQL]\n"
            f"### TARGET TASK ###\n"
            f"Question: {question}\n"
            f"Schema: {schema}\n\n"
            f"### SYSTEM RESPONSE ###\n"
            f"Analysis:"
        )
    else:
        raise ValueError(f"Unsupported validation routing task category: {task_type}")