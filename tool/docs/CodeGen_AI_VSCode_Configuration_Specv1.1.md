# CodeGen AI Extension - Change Specification (v1.1)

## Purpose

This document describes the architectural changes introduced after Version 1.0.

The primary enhancement is the addition of a **Database Execution Layer**, allowing the extension to execute generated queries and present results directly within VS Code.

This version also clarifies that the system is **not an AI agent**. Instead, it implements a deterministic Retrieval-Augmented Prompt Orchestration pipeline.

---

# 1. Architecture Update

## Previous Architecture

```
User

↓

VS Code Chat

↓

CodeGen Extension

↓

Prompt Builder

↓

Hugging Face Endpoint

↓

Generated SQL

```

---

## Updated Architecture

```
User

↓

VS Code Chat

↓

CodeGen Extension

├── Workspace Scanner

├── Schema Parser

├── Embedding Engine

├── Vector Search

├── Intent Detector

├── Schema Retriever

├── Prompt Builder

├── Hugging Face Client

├── SQL Validator

├── Database Executor

└── Result Renderer

↓

Hugging Face Endpoint

↓

CodeGen Multi Adapter

↓

Generated SQL

↓

Validation

↓

Database Execution

↓

Result Rendering

```

---

# 2. Design Decision

## No AI Agent

This project intentionally avoids agent frameworks.

Examples:

- LangGraph
- CrewAI
- AutoGen

Reason:

The workflow is deterministic.

Every request follows a predefined pipeline.

There is no autonomous planning or iterative reasoning.

---

## Pipeline

```
User Question

↓

Intent Detection

↓

Schema Retrieval

↓

Prompt Construction

↓

Model Inference

↓

SQL Validation

↓

Database Execution

↓

Display Results

```

Each stage has a single responsibility.

---

# 3. New Components

## SQL Validator

### Responsibility

Validate generated SQL before execution.

Checks include:

- Syntax validation
- Empty query detection
- Read-only enforcement (optional)
- Unsupported statements
- Dangerous commands

Initial supported statements

- SELECT

Future

- INSERT
- UPDATE
- DELETE
- Stored Procedures

---

## Database Executor

### Responsibility

Execute validated SQL against the configured database.

Supported databases (Phase 1)

- SQLite

Future

- PostgreSQL
- MySQL
- SQL Server
- Oracle
- Snowflake

Interface

```
execute(sql): QueryResult

```

---

## Result Renderer

### Responsibility

Display execution results inside VS Code.

Display:

- Generated SQL
- Execution time
- Returned rows
- Column names
- Number of rows

Future

- Export CSV
- Export Excel
- Pagination
- Charts

---

# 4. Extension Workflow

## Previous

```
Question

↓

Generate SQL

↓

Return SQL

```

---

## New

```
Question

↓

Retrieve Schemas

↓

Generate SQL

↓

Validate SQL

↓

Execute SQL

↓

Render Results

```

---

# 5. Prompt Builder

No change.

The Prompt Builder continues to generate prompts containing:

- Task
- Schema
- User Question

The model remains stateless.

---

# 6. Database Configuration

New extension settings.

```
codegen.database.enabled

codegen.database.type

codegen.database.connection

codegen.database.readOnly

codegen.database.timeout

codegen.database.maxRows

```

Example

```json
{
  "codegen.database.enabled": true,
  "codegen.database.type": "sqlite",
  "codegen.database.connection": "/workspace/sample.db",
  "codegen.database.readOnly": true,
  "codegen.database.timeout": 30000,
  "codegen.database.maxRows": 100
}

```

---

# 7. Database Abstraction

Create a common interface.

```
DatabaseProvider

connect()

disconnect()

execute(sql)

validate(sql)

```

Implementations

```
SQLiteProvider

PostgresProvider

MySQLProvider

MongoProvider (future)

```

---

# 8. VS Code Commands

New commands

```
CodeGen: Connect Database

CodeGen: Disconnect Database

CodeGen: Test Connection

CodeGen: Execute Generated SQL

CodeGen: View Query History

```

---

# 9. Chat Experience

User asks

```
How many singers do we have?

```

Extension displays

```
Detected Intent

✓ text2sql

Retrieved Schemas

✓ singer

Generated SQL

SELECT COUNT(*)
FROM singer;

Validation

✓ Passed

Execution

✓ Success

Execution Time

14 ms

Result

+-------+
| count |
+-------+
| 37    |
+-------+

```

---

# 10. Query History

Maintain a local history.

Store

- Question
- Retrieved Schemas
- Generated SQL
- Execution Status
- Execution Time
- Result Count
- Timestamp

Purpose

- Demonstration
- Debugging
- Performance Evaluation

---

# 11. Security

Default mode

Read-only.

Blocked statements

- DROP
- DELETE
- TRUNCATE
- ALTER
- CREATE
- INSERT
- UPDATE
- MERGE

Only SELECT statements are executed unless explicitly enabled.

---

# 12. Performance Metrics

Capture

- Schema Retrieval Time
- Prompt Build Time
- Model Inference Time
- SQL Validation Time
- Database Execution Time
- Total Request Time

Display these metrics in a debug view for demonstrations.

---

# 13. Logging

Additional logs

```
Database Connected

Query Executed

Execution Failed

Validation Failed

Rows Returned

```

---

# 14. Updated Folder Structure

```
src/

database/

    databaseProvider.ts

    sqliteProvider.ts

    postgresProvider.ts

    validator.ts

renderer/

    resultRenderer.ts

history/

    queryHistory.ts

```

---

# 15. Updated Milestones

## Milestone 1

Extension Skeleton

---

## Milestone 2

Workspace Scanner

---

## Milestone 3

Embedding Index

---

## Milestone 4

Schema Retrieval

---

## Milestone 5

Prompt Builder

---

## Milestone 6

Hugging Face Integration

---

## Milestone 7

SQL Validation

---

## Milestone 8

Database Execution Layer

---

## Milestone 9

Result Rendering

---

## Milestone 10

Query History, Metrics, and Performance Dashboard

---

# 16. Updated Acceptance Criteria

A successful demonstration should follow this sequence:

1. User opens a project.
2. Extension indexes repository schemas.
3. User asks a natural language question.
4. Extension detects the intent.
5. Extension retrieves the relevant schema.
6. Extension constructs the complete prompt.
7. Prompt is sent to the Hugging Face OpenAI-compatible endpoint.
8. The model generates SQL.
9. The extension validates the generated SQL.
10. The extension executes the SQL against the configured database.
11. Results are rendered in VS Code.
12. Execution metrics and query history are recorded.

---

# 17. Capstone Positioning

The project should be presented as:

> **An IDE-Integrated Retrieval-Augmented Prompt Orchestration Framework with Automatic Database Query Execution for Adapter-Based Code Generation**

The major contributions are:

- Multi-adapter fine-tuned CodeGen model.
- Automatic schema retrieval using semantic search.
- Repository-aware prompt augmentation.
- Native IDE integration.
- Safe database execution with read-only validation.
- End-to-end developer workflow from natural language to verified database results.

