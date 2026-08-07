"""
One-time script to build the retrieval index from training data.
Run this once before using --rag inference:

    python scripts/build_retrieval_index.py
    python scripts/build_retrieval_index.py --task text2sql
    python scripts/build_retrieval_index.py --task sql2nosql
    python scripts/build_retrieval_index.py --task text2nosql

Outputs:
    retrieval_index/text2sql_embeddings.npy     (N x 384) float32, L2-normalised
    retrieval_index/text2sql_metadata.json
    retrieval_index/sql2nosql_embeddings.npy    (M x 384) float32, L2-normalised
    retrieval_index/sql2nosql_metadata.json
    retrieval_index/text2nosql_embeddings.npy   (K x 384) float32, L2-normalised
    retrieval_index/text2nosql_metadata.json

IMPORTANT: Only training data enters the index.
           Test data (Spider dev, DocSpider dev) is never embedded.
"""

import argparse
import json
import os
import sys
import numpy as np

# Allow running from project root
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.config import DATA

RETRIEVAL_INDEX_DIR = "retrieval_index"
BGE_MODEL_ID = "BAAI/bge-small-en-v1.5"


def _load_bge_model():
    try:
        from sentence_transformers import SentenceTransformer
    except ImportError:
        print("sentence-transformers not found. Install with:")
        print("  pip install sentence-transformers>=2.7.0")
        sys.exit(1)
    print(f"[build_index] Loading {BGE_MODEL_ID}...")
    return SentenceTransformer(BGE_MODEL_ID)


def build_text2sql_index(model):
    """Embed Spider training questions for text2sql retrieval."""
    train_path = DATA["spider_train"]
    tables_path = DATA["spider_tables"]

    if not os.path.exists(train_path):
        raise FileNotFoundError(f"Spider train not found: {train_path}")
    if not os.path.exists(tables_path):
        raise FileNotFoundError(f"Spider tables not found: {tables_path}")

    with open(train_path, "r", encoding="utf-8") as f:
        train_data = json.load(f)
    with open(tables_path, "r", encoding="utf-8") as f:
        tables_raw = json.load(f)

    table_names_map = {db["db_id"]: db["table_names_original"] for db in tables_raw}

    texts = []
    metadata = []
    for entry in train_data:
        question = entry.get("question", "").strip()
        db_id = entry.get("db_id", "")
        gold_sql = entry.get("query", "").strip()
        if not question or not gold_sql:
            continue
        table_names = table_names_map.get(db_id, [])
        table_str = ", ".join(table_names)
        texts.append(f"{question} | contexts: {table_str}")
        metadata.append({
            "question": question,
            "db_id": db_id,
            "gold_sql": gold_sql,
            "table_names": table_names,
        })

    print(f"[build_index] Encoding {len(texts)} text2sql training examples...")
    embeddings = model.encode(
        texts, batch_size=64, show_progress_bar=True, normalize_embeddings=True
    )

    os.makedirs(RETRIEVAL_INDEX_DIR, exist_ok=True)
    emb_path = os.path.join(RETRIEVAL_INDEX_DIR, "text2sql_embeddings.npy")
    meta_path = os.path.join(RETRIEVAL_INDEX_DIR, "text2sql_metadata.json")

    np.save(emb_path, embeddings.astype("float32"))
    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2)

    print(f"[build_index] text2sql index: {embeddings.shape} → {emb_path}")


def build_sql2nosql_index(model):
    """Embed DocSpider training SQL queries for sql2nosql retrieval."""
    train_path = DATA["docspider_train"]

    if not os.path.exists(train_path):
        raise FileNotFoundError(f"DocSpider train not found: {train_path}")

    with open(train_path, "r", encoding="utf-8") as f:
        raw_data = json.load(f)

    texts = []
    metadata = []
    for entry in raw_data:
        sql = entry.get("spider_gold_sql", "").strip()
        mql = entry.get("query", "").strip()
        db_id = entry.get("db_id", "")
        if not sql or not mql:
            continue
        texts.append(sql)
        metadata.append({
            "spider_gold_sql": sql,
            "db_id": db_id,
            "query": mql,  # Aligned key hook for prompt builder extraction
            "gold_mql": mql,
        })

    print(f"[build_index] Encoding {len(texts)} sql2nosql training examples...")
    embeddings = model.encode(
        texts, batch_size=64, show_progress_bar=True, normalize_embeddings=True
    )

    os.makedirs(RETRIEVAL_INDEX_DIR, exist_ok=True)
    emb_path = os.path.join(RETRIEVAL_INDEX_DIR, "sql2nosql_embeddings.npy")
    meta_path = os.path.join(RETRIEVAL_INDEX_DIR, "sql2nosql_metadata.json")

    np.save(emb_path, embeddings.astype("float32"))
    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2)

    print(f"[build_index] sql2nosql index: {embeddings.shape} → {emb_path}")


def build_text2nosql_index(model):
    """Embed DocSpider training questions for text2nosql direct retrieval."""
    train_path = DATA["docspider_train"]
    collections_path = DATA.get("docspider_collections", "data/docspider/collections.json")

    if not os.path.exists(train_path):
        raise FileNotFoundError(f"DocSpider train file not found: {train_path}")
    if not os.path.exists(collections_path):
        raise FileNotFoundError(f"DocSpider collections context map file not found: {collections_path}")

    with open(train_path, "r", encoding="utf-8") as f:
        train_data = json.load(f)
    with open(collections_path, "r", encoding="utf-8") as f:
        collections_raw = json.load(f)

    collection_names_map = {db["db_id"]: db["collection_names"] for db in collections_raw}

    texts = []
    metadata = []
    for entry in train_data:
        question = entry.get("question", "").strip()
        db_id = entry.get("db_id", "")
        mql = entry.get("query", "").strip()
        if not question or not mql:
            continue
            
        collection_names = collection_names_map.get(db_id, [])
        collection_str = ", ".join(collection_names)
        
        # Matches retriever.py structural lookups exactly
        texts.append(f"{question} | contexts: {collection_str}")
        metadata.append({
            "question": question,
            "db_id": db_id,
            "query": mql,
            "collection_names": collection_names,
        })

    print(f"[build_index] Encoding {len(texts)} text2nosql training examples...")
    embeddings = model.encode(
        texts, batch_size=64, show_progress_bar=True, normalize_embeddings=True
    )

    os.makedirs(RETRIEVAL_INDEX_DIR, exist_ok=True)
    emb_path = os.path.join(RETRIEVAL_INDEX_DIR, "text2nosql_embeddings.npy")
    meta_path = os.path.join(RETRIEVAL_INDEX_DIR, "text2nosql_metadata.json")

    np.save(emb_path, embeddings.astype("float32"))
    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2)

    print(f"[build_index] text2nosql index: {embeddings.shape} → {emb_path}")


def build_spider_schema_index(model):
    """
    Embed each Spider table as 'table_name col1 col2 ...' for schema pruning.
    Outputs schema_spider_embeddings.npy + schema_spider_metadata.json.
    """
    tables_path = DATA["spider_tables"]
    if not os.path.exists(tables_path):
        raise FileNotFoundError(f"Spider tables not found: {tables_path}")

    with open(tables_path, "r", encoding="utf-8") as f:
        tables_data = json.load(f)

    texts    = []
    metadata = []
    for db in tables_data:
        db_id       = db["db_id"]
        table_names = db["table_names_original"]
        col_names   = db["column_names_original"]

        table_cols = {i: [] for i in range(len(table_names))}
        for table_idx, col_name in col_names:
            if table_idx != -1:
                table_cols[table_idx].append(col_name)

        for idx, t_name in enumerate(table_names):
            cols_str   = " ".join(table_cols[idx])
            table_str  = f"{t_name} {cols_str}".strip()
            texts.append(table_str)
            metadata.append({"db_id": db_id, "name": t_name, "table_str": table_str})

    print(f"[build_index] Encoding {len(texts)} Spider tables for schema pruning...")
    embeddings = model.encode(
        texts, batch_size=64, show_progress_bar=True, normalize_embeddings=True
    )

    os.makedirs(RETRIEVAL_INDEX_DIR, exist_ok=True)
    np.save(os.path.join(RETRIEVAL_INDEX_DIR, "schema_spider_embeddings.npy"),
            embeddings.astype("float32"))
    with open(os.path.join(RETRIEVAL_INDEX_DIR, "schema_spider_metadata.json"),
              "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2)

    print(f"[build_index] Spider schema index: {embeddings.shape} → retrieval_index/schema_spider_*")


def build_docspider_schema_index(model):
    """
    Embed each DocSpider collection as 'collection_name field1 field2 ...' for schema pruning.
    Outputs schema_docspider_embeddings.npy + schema_docspider_metadata.json.
    """
    collections_path = DATA["docspider_collections"]
    if not os.path.exists(collections_path):
        raise FileNotFoundError(f"DocSpider collections not found: {collections_path}")

    with open(collections_path, "r", encoding="utf-8") as f:
        colls_data = json.load(f)

    texts    = []
    metadata = []
    for db in colls_data:
        db_id      = db["db_id"]
        coll_names = db["collection_names"]
        col_names  = db["column_names"]

        grouped = {i: [] for i in range(len(coll_names))}
        for col in col_names:
            col_idx, col_name = col[0], col[1]
            if col_idx in grouped:
                grouped[col_idx].append(col_name)

        for idx, coll_name in enumerate(coll_names):
            fields_str = " ".join(grouped[idx])
            table_str  = f"{coll_name} {fields_str}".strip()
            texts.append(table_str)
            metadata.append({"db_id": db_id, "name": coll_name, "table_str": table_str})

    print(f"[build_index] Encoding {len(texts)} DocSpider collections for schema pruning...")
    embeddings = model.encode(
        texts, batch_size=64, show_progress_bar=True, normalize_embeddings=True
    )

    os.makedirs(RETRIEVAL_INDEX_DIR, exist_ok=True)
    np.save(os.path.join(RETRIEVAL_INDEX_DIR, "schema_docspider_embeddings.npy"),
            embeddings.astype("float32"))
    with open(os.path.join(RETRIEVAL_INDEX_DIR, "schema_docspider_metadata.json"),
              "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2)

    print(f"[build_index] DocSpider schema index: {embeddings.shape} → retrieval_index/schema_docspider_*")


def main():
    parser = argparse.ArgumentParser(description="Build retrieval index from training data")
    parser.add_argument(
        "--task",
        choices=["text2sql", "sql2nosql", "text2nosql", "schema"],
        default=None,
        help="Which index to build. Omit to build all. 'schema' builds the schema-pruning index.",
    )
    args = parser.parse_args()

    model = _load_bge_model()

    build_all = args.task is None
    task = args.task

    if build_all or task == "text2sql":
        build_text2sql_index(model)
    if build_all or task == "sql2nosql":
        build_sql2nosql_index(model)
    if build_all or task == "text2nosql":
        build_text2nosql_index(model)
    if build_all or task == "schema":
        build_spider_schema_index(model)
        build_docspider_schema_index(model)

    print("\n[build_index] Done.")


if __name__ == "__main__":
    main()