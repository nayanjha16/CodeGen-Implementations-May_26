# TEND-Style Dataset Generation Plan Using SPIDER/BIRD

## Project Objective

Create a TEND-style dataset for Text-to-NoSQL training using SPIDER or BIRD datasets as the source.

The final dataset should contain:

| Field        | Description                                   |
| ------------ | --------------------------------------------- |
| sql_schema   | Original relational database schema           |
| sql_query    | Original SQL query                            |
| nosql_schema | Equivalent MongoDB schema                     |
| nosql_query  | Equivalent MongoDB query                      |
| metadata     | Dataset source, complexity, database id, etc. |

Example:

```json
{
  "dataset": "bird",
  "db_id": "university",
  "difficulty": "medium",
  "sql_schema": "...",
  "sql_query": "...",
  "nosql_schema": "...",
  "nosql_query": "..."
}
```

---

# Phase 1: Dataset Selection and Analysis

## Option 1: SPIDER Dataset

### Advantages

* High-quality SQL annotations
* Widely used benchmark
* Easier SQL-to-MongoDB conversion
* Suitable for initial development

### Disadvantages

* Smaller dataset (~10K queries)
* Less realistic enterprise schemas

---

## Option 2: BIRD Dataset

### Advantages

* Larger dataset
* Real-world database schemas
* More diverse SQL patterns

### Disadvantages

* More complex SQL
* Higher conversion failure rate

---

## Recommendation

### Stage 1 (MVP)

Use SPIDER dataset.

### Stage 2 (Scaling)

Extend pipeline to BIRD dataset.

---

# Phase 2: SQL Schema Extraction

## Goal

Convert SPIDER/BIRD schema definitions into SQL DDL format.

### Input

Dataset schema JSON:

```json
{
  "table_names": ["student", "course"],
  "column_names": [...]
}
```

### Output

```sql
CREATE TABLE student (
    id INT,
    name VARCHAR(100)
);

CREATE TABLE course (
    id INT,
    title VARCHAR(100)
);
```

---

## Deliverable

### File

```text
schema_to_sql.py
```

### Function

```python
generate_sql_schema(db_json)
```

### Output

```python
sql_schema
```

---

# Phase 3: SQL Schema to MongoDB Schema Conversion

## Goal

Generate an equivalent MongoDB schema representation.

---

## Schema Mapping Rules

### Single Table

SQL:

```sql
CREATE TABLE student (
    id INT,
    name TEXT,
    age INT
);
```

MongoDB:

```json
{
  "student": {
    "_id": "ObjectId",
    "name": "string",
    "age": "number"
  }
}
```

---

### One-to-Many Relationship

SQL:

```text
student
course
```

MongoDB:

```json
{
  "student": {
    "_id": "...",
    "courses": [
      {
        "course_id": "...",
        "title": "..."
      }
    ]
  }
}
```

---

### Many-to-Many Relationship

SQL:

```text
student
enrollment
course
```

MongoDB Option 1:

```json
{
  "student": {
    "courses": [
      {
        "course_id": "...",
        "title": "..."
      }
    ]
  }
}
```

MongoDB Option 2:

```json
{
  "enrollment": {
    "student_id": "...",
    "course_id": "..."
  }
}
```

Selection should be based on configurable conversion heuristics.

---

## Deliverable

### File

```text
sql_schema_to_mongo_schema.py
```

### Function

```python
convert_schema(sql_schema)
```

### Output

```json
{
  "student": {
    "_id": "ObjectId",
    "name": "string"
  }
}
```

---

# Phase 4: SQL Query to MongoDB Query Conversion

## Conversion Engine

Repository:

https://github.com/hoangsonww/SQL-Mongo-Query-Converter

---

## Setup

```bash
git clone https://github.com/hoangsonww/SQL-Mongo-Query-Converter.git

pip install -r requirements.txt
```

---

## Example

SQL:

```sql
SELECT name
FROM student
WHERE age > 20;
```

MongoDB:

```javascript
db.student.find(
  { age: { $gt: 20 } },
  { name: 1 }
)
```

---

## Deliverable

### File

```text
sql_to_mongo.py
```

### Function

```python
convert_query(sql_query)
```

### Output

```javascript
Mongo query
```

---

# Phase 5: Dataset Generation Pipeline

## End-to-End Workflow

```text
SPIDER / BIRD
      │
      ▼
Schema Extractor
      │
      ▼
SQL Schema
      │
      ├────────────► Mongo Schema Converter
      │                     │
      │                     ▼
      │               Mongo Schema
      │
      ▼
SQL Query
      │
      ▼
SQL-Mongo Converter
      │
      ▼
Mongo Query
      │
      ▼
Dataset Builder
      │
      ▼
Final Dataset
```

---

## Dataset Builder

### File

```text
build_tend_dataset.py
```

### Pseudocode

```python
for sample in dataset:

    sql_schema = generate_sql_schema(sample)

    mongo_schema = convert_schema(sql_schema)

    mongo_query = convert_query(sample.sql)

    save(
        sql_schema,
        sample.sql,
        mongo_schema,
        mongo_query
    )
```

---

# Phase 6: Validation Framework

## Objective

Ensure generated schema and query pairs are valid and usable.

---

## Validation Checks

### SQL Schema Validation

```python
validate_sql_schema()
```

### SQL Query Validation

```python
validate_sql_query()
```

### Mongo Schema Validation

```python
validate_mongo_schema()
```

### Mongo Query Validation

```python
validate_mongo_query()
```

### Conversion Success

```python
mongo_query is not None
```

---

## Expected Dataset Retention

### SPIDER

| Stage             | Samples |
| ----------------- | ------- |
| Original          | ~10,181 |
| SQL→Mongo Success | 85–95%  |
| Final Dataset     | 8K–9K   |

### BIRD

| Stage             | Samples                        |
| ----------------- | ------------------------------ |
| Original          | Larger                         |
| SQL→Mongo Success | 60–80%                         |
| Final Dataset     | Depends on conversion coverage |

---

# Phase 7: Dataset Enrichment

Add useful metadata for model training and evaluation.

Example:

```json
{
  "source": "spider",
  "db_id": "college",
  "difficulty": "hard",
  "tables": 4,
  "joins": 2,
  "aggregations": 1,
  "sql_schema": "...",
  "sql_query": "...",
  "nosql_schema": "...",
  "nosql_query": "..."
}
```

---

# Phase 8: Dataset Quality Evaluation

## Coverage Metric

```text
Converted Queries / Total Queries
```

---

## Schema Accuracy

Manual review:

```text
100 random samples
```

---

## Query Equivalence

Execute both SQL and MongoDB queries against equivalent databases.

Validation:

```python
result_sql == result_mongo
```

---

# Recommended Repository Structure

```text
text-to-nosql-dataset/
│
├── data/
│   ├── spider/
│   ├── bird/
│   └── generated/
│
├── src/
│   ├── schema_to_sql.py
│   ├── sql_schema_to_mongo_schema.py
│   ├── sql_to_mongo.py
│   ├── validator.py
│   └── build_tend_dataset.py
│
├── outputs/
│   ├── train.json
│   ├── dev.json
│   └── test.json
│
├── notebooks/
│
└── docs/
    └── TEND_Dataset_Generation_Plan.md
```

---

# Project Milestones

## Milestone 1

* Download SPIDER/BIRD datasets
* Parse schemas
* Generate SQL schema representation

---

## Milestone 2

* Build SQL Schema → MongoDB Schema converter
* Define schema mapping heuristics

---

## Milestone 3

* Integrate SQL-Mongo-Query-Converter
* Generate MongoDB queries

---

## Milestone 4

* Build dataset generation pipeline
* Produce first TEND-style dataset

---

## Milestone 5

* Implement validation framework
* Measure conversion coverage and quality

---

## Milestone 6

* Train and evaluate Text-to-NoSQL model
* Compare baseline vs fine-tuned performance

---

# Final Dataset Format

Each sample should contain:

```json
{
  "sql_schema": "...",
  "sql_query": "...",
  "nosql_schema": "...",
  "nosql_query": "...",
  "source": "spider",
  "db_id": "...",
  "difficulty": "...",
  "metadata": {}
}
```

This dataset can be directly used for:

* Text-to-NoSQL model training
* Fine-tuning CodeT5/T5 models
* RAG-based query generation
* Agent-based database querying systems
* Benchmarking Text-to-NoSQL research

```
```
