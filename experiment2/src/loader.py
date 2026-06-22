import json
import os
from src.config import TABLES_PATH

def load_spider_schema_maps():
    """
    Reads tables.json and builds a highly recognizable SQL DDL Schema string for each database:
    CREATE TABLE table_name (
        col1 text,
        col2 int
    );
    """
    if not os.path.exists(TABLES_PATH):
        raise FileNotFoundError(f"❌ Tables schema file not found at: {TABLES_PATH}")
        
    with open(TABLES_PATH, "r", encoding="utf-8") as f:
        tables_data = json.load(f)
        
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
        
    return schema_map


def load_spider_tasks(dataset_path, limit=None):
    """
    Reads the official Spider dev.json list array.
    """
    if not os.path.exists(dataset_path):
        raise FileNotFoundError(f"❌ Core dataset file not found at: {dataset_path}")

    with open(dataset_path, "r", encoding="utf-8") as f:
        tasks = json.load(f)
        
    if limit:
        return tasks[:limit]
    return tasks

  
def construct_zero_shot_prompt(task, schema_map):
    """
    Wraps the DDL database schema inside standard comment tags, leaving
    the query area perfectly un-commented to prompt strict code autocomplete.
    """
    db_id = task.get("db_id", "unknown_db")
    question = task.get("question", "")
    ddl_schema = schema_map.get(db_id, "-- Schema unavailable")
    
    prompt = (
        f"/* Given the following database schema: */\n"
        f"{ddl_schema}\n\n"
        f"/* Answer the question: {question} */\n"
        f"SELECT"
    )
    return prompt
    
def construct_one_shot_prompt(task, schema_map):
    """
    An upgraded 'Swiss Army Knife' static prompt template that demonstrates 
    multiple complex SQL operations (JOIN, Aggregate, and ORDER BY) to prevent 
    the model from over-indexing on a single simple clause pattern.
    """
    db_id = task.get("db_id", "unknown_db")
    question = task.get("question", "")
    ddl_schema = schema_map.get(db_id, "-- Schema unavailable")
    
    demo_schema = (
        "CREATE TABLE student (\n"
        "    student_id int,\n"
        "    name text,\n"
        "    age int,\n"
        "    major_id int\n"
        ");\n"
        "CREATE TABLE major (\n"
        "    major_id int,\n"
        "    major_name text\n"
        ");"
    )
    demo_question = "Find the total number of students in each major, sorted from highest to lowest enrollment count."
    demo_sql = "SELECT T2.major_name, COUNT(T1.student_id) FROM student AS T1 JOIN major AS T2 ON T1.major_id = T2.major_id GROUP BY T2.major_name ORDER BY COUNT(T1.student_id) DESC;"

    prompt = (
        f"/* Example Task Mapping */\n"
        f"/* Database Schema: */\n{demo_schema}\n"
        f"/* Question: {demo_question} */\n"
        f"SQL: {demo_sql}\n\n"
        f"/* Target Task Mapping */\n"
        f"/* Database Schema: */\n{ddl_schema}\n"
        f"/* Question: {question} */\n"
        f"SQL: SELECT"
    )
    return prompt

# =====================================================================
# STAGE 3 FINE-TUNED PROMPT ROUTINE (NEW)
# =====================================================================
def construct_stage3_prompt(task):
    """
    Generates the precise structural format that your LoRA adapter 
    learned to expect during its 3 training epochs in Colab.
    """
    db_id = task.get("db_id", "")
    question = task.get("question", "")
    
    prompt = (
        f"### Instruction:\n"
        f"Convert this question to SQL for database: {db_id}\n"
        f"### Question:\n"
        f"{question}\n"
        f"### Response:\n"
    )
    return prompt
    
    
# =====================================================================
# EXPERIMENT 2: MODULAR PIPELINE PROMPT ROUTINE (NEW)
# =====================================================================
import json

def load_schema_context_map(collections_json_path):
    """
    Parses collections.json into a structural scannable text mapping:
    db_id -> "Collection1(field1, field2) | Collection2(field1)"
    """
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
    return schema_map

def construct_nosql_prompt(sql_query, db_id, schema_context_map):
    """
    Constructs a schema-grounded prompt matching the fine-tuning format exactly.
    """
    schema_info = schema_context_map.get(db_id, "Unknown schema footprint")
    
    prompt = (
        f"### Instruction:\n"
        f"Using the database schema provided, translate the SQL query into an executable MongoDB NoSQL query.\n"
        f"### Schema:\n{schema_info}\n"
        f"### SQL:\n{sql_query}\n"
        f"### Response:\n"
    )
    return prompt
