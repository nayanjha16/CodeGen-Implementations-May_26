# AI SQL Assistant -- UI & Functional Specification

**Version:** 1.1\
**Purpose:** Define the UI, workflow, and functional requirements for a
lightweight, extensible AI-powered SQL assistant (Text-to-SQL first;
SQL-to-NoSQL as a future tab).

------------------------------------------------------------------------

# 1. Objective

Build a Python application that:

1.  Accepts a natural language query (Text-to-SQL tab) or SQL input (SQL-to-NoSQL tab, future).
2.  Reads the connected database schema.
3.  Uses a fine-tuned model to generate the target query.
4.  Displays the generated query.
5.  Validates the query.
6.  Executes the query.
7.  Displays the results in a scrollable table.
8.  Shows a structured activity panel with as many observable system events as possible.

The activity panel must display **observable system events only**. It
must never display internal model reasoning.

The tool must be **extensible by design** so that Text-to-SQL and
SQL-to-NoSQL (and related documentation demos) can coexist as separate
tabs within the same application shell.

------------------------------------------------------------------------

# 2. Technology Stack

  Layer            Technology
  ---------------- ----------------------------------------------
  UI               CustomTkinter (native desktop application)
  Backend          Python
  Database         PostgreSQL (via SQLAlchemy)
  AI Model         Fine-tuned Hugging Face Model (LoRA Adapter)
  Data Display     Pandas
  SQL Formatting   sqlparse

Charts and visualization libraries are **not required**. Query output
(table) is sufficient for results display.

------------------------------------------------------------------------

# 3. Application Shell & Tab Architecture

The application uses a **tab-based layout** so new capabilities can be
added without restructuring the UI.

    +------------------------------------------------------------------------------------------------------+
    | AI SQL Assistant                                            PostgreSQL ● Connected                   |
    +------------------------------------------------------------------------------------------------------+
    | [ Text-to-SQL ]  [ SQL-to-NoSQL ]  [ Documentation ]                                                 |
    +---------------------------------------------------------------------------------------+--------------+
    | Main Workspace (active tab content)                                                   | Activity Log |
    |                                                                                       |              |
    | ... tab-specific panels ...                                                           | Structured   |
    |                                                                                       | live events  |
    +---------------------------------------------------------------------------------------+--------------+

## Tab Definitions

### Text-to-SQL (primary tab)

- Natural language input → generate SQL → validate → execute → show results.
- Full workflow described in Sections 4–5.

### SQL-to-NoSQL (future tab)

- SQL input → generate NoSQL query (e.g. MongoDB, DynamoDB) → validate → execute (when adapter available) → show results.
- Reuses the same activity logger, validation pattern, output panel, and execute workflow.
- Implemented via a pluggable **adapter** interface (see Section 6).

### Documentation (optional tab)

- In-tab demo or reference content for the active capability (usage examples, supported dialects, safety rules).
- Can be embedded inside a capability tab or exposed as its own tab; the shell must support either pattern.

Each tab shares:

- Connection status header
- Activity log panel
- Output panel conventions (scrollable table, view-only results)
- Single **Execute** action pattern

------------------------------------------------------------------------

# 4. Screen Layout (Text-to-SQL Tab)

    +------------------------------------------------------------------------------------------------------+
    | AI SQL Assistant                                            PostgreSQL ● Connected                   |
    +------------------------------------------------------------------------------------------------------+
    | [ Text-to-SQL ]  [ SQL-to-NoSQL ]  [ Documentation ]                                                 |
    +---------------------------------------------------------------------------------------+--------------+
    | Main Workspace                                                                        | Activity Log |
    |                                                                                       |              |
    | Natural Language Query                                                                | Structured   |
    | +------------------------------------------------------------+                        | events       |
    | | Show top customers by sales                                |                        | (JSON-like   |
    | +------------------------------------------------------------+                        |  blocks)     |
    | [ Execute ]  [ Clear ]                                                                |              |
    |---------------------------------------------------------------------------------------|--------------|
    | Generated SQL                                                                         |              |
    | +------------------------------------------------------------+                        |              |
    | | SELECT ...                                                  |                        |              |
    | +------------------------------------------------------------+                        |              |
    |---------------------------------------------------------------------------------------|--------------|
    | Execution Output                                                                      |              |
    | +------------------------------------------------------------+                        |              |
    | | Result Table (scrollable, view-only)                        |                        |              |
    | | +--------------------------------------------------------+  |                        |              |
    | | | col_a | col_b | col_c | ...                            |  |                        |              |
    | | | ...   | ...   | ...   | ...                            |  |                        |              |
    | | +--------------------------------------------------------+  |                        |              |
    | +------------------------------------------------------------+                        |              |
    +---------------------------------------------------------------------------------------+--------------+

------------------------------------------------------------------------

# 5. Main Components

## A. Natural Language Query

-   Multi-line text box
-   Example placeholder
-   Keyboard shortcut (Ctrl/Cmd + Enter triggers **Execute**)
-   Buttons:
    -   **Execute** — single action that generates SQL, validates it, and runs it (see Section 6)
    -   **Clear** — resets query, generated SQL, results, and optionally clears the activity log

There is **no separate "Generate SQL" button**. One Execute action covers
generation and execution end-to-end.

------------------------------------------------------------------------

## B. Generated SQL

-   Read-only editor
-   Syntax highlighting
-   Copy SQL button (optional convenience; no file download required)
-   SQL validation status (shown inline after Execute)

Generated SQL is displayed **after** Execute completes the generation
step and **before** or **during** execution; the user sees the query on
the same screen without a separate generate step.

------------------------------------------------------------------------

## C. Execution Output

Display:

-   **Scrollable result table** — fixed-height container with vertical
    (and horizontal, if needed) scroll; full row/column set visible
    within the scroll area
-   Number of rows
-   Execution time

**View only.** No CSV, Excel, or other download actions for results.
No charts or auto-generated visualizations.

------------------------------------------------------------------------

## D. Activity Panel (Structured Logs)

The activity panel must surface **as many observable events as
practically possible** from every pipeline stage. Events are shown in a
**structured format** (not plain unstructured text), so each entry is
easy to scan, filter, and extend.

### Structured event shape

Each log entry should include, where applicable:

| Field        | Description                                      |
| ------------ | ------------------------------------------------ |
| `timestamp`  | Relative or absolute time                        |
| `level`      | `info` \| `success` \| `warning` \| `error`      |
| `stage`      | Pipeline stage (e.g. `schema`, `model`, `exec`) |
| `event`      | Short event name                                 |
| `message`    | Human-readable summary                           |
| `details`    | Optional key-value payload (tables, counts, etc.) |

### Example (structured display)

```json
{
  "timestamp": "00:00.050",
  "level": "info",
  "stage": "schema",
  "event": "schema_loaded",
  "message": "Found 24 tables",
  "details": { "table_count": 24, "duration_ms": 32 }
}
```

```json
{
  "timestamp": "00:00.122",
  "level": "info",
  "stage": "schema",
  "event": "tables_selected",
  "message": "Selected relevant tables",
  "details": { "tables": ["Customers", "Orders"] }
}
```

```json
{
  "timestamp": "00:01.102",
  "level": "success",
  "stage": "model",
  "event": "sql_generated",
  "message": "SQL generated",
  "details": { "duration_ms": 462, "token_count": 128 }
}
```

### Events to emit (non-exhaustive; maximize coverage)

- Connection established / failed
- Schema read start / complete (table count, duration)
- Relevant tables identified (names, method if applicable)
- Prompt built (template id, input length)
- Model load / inference start / complete (duration, token stats if available)
- SQL generated (length, dialect)
- Validation start / passed / failed (rule id, reason)
- Execution start / complete (row count, duration, truncated flag)
- Result render start / complete
- Errors at any stage (stage, code, message)

The log should **auto-scroll** to the latest entry. The panel should
remain readable when many events are emitted (compact structured rows or
collapsible detail blocks).

The activity panel must display **observable system events only**. It
must never display internal model reasoning or chain-of-thought.

------------------------------------------------------------------------

# 6. End-to-End Workflow

## Single Execute action (Text-to-SQL)

    User
      |
      v
    Enter Natural Language Query
      |
      v
    Click Execute (or Ctrl/Cmd + Enter)
      |
      v
    Connect to Database (if not connected)
      |
      v
    Load Schema                    --> log
      |
      v
    Identify Relevant Tables       --> log
      |
      v
    Build Prompt                   --> log
      |
      v
    Fine-tuned Text-to-SQL Model   --> log
      |
      v
    Generate SQL                   --> display in SQL panel
      |
      v
    Validate SQL                   --> log
      |
      v
    Execute SQL                    --> log
      |
      v
    Display Results (scrollable table, view-only)

If generation or validation fails, execution does not proceed; errors
appear in the activity log and inline near the SQL panel.

## Future: SQL-to-NoSQL tab

Same **Execute** pattern: SQL in → generate NoSQL → validate → execute
(when supported) → scrollable view-only results, with full structured
logging at each stage.

------------------------------------------------------------------------

# 7. Backend Modules

    project/
    │
    ├── app.py                      # Tab shell, routing
    ├── database.py
    ├── schema.py
    ├── prompt_builder.py
    ├── model.py
    ├── validator.py
    ├── executor.py
    ├── activity_logger.py          # Structured event API
    ├── ui/
    │   ├── tabs/
    │   │   ├── text2sql_tab.py
    │   │   ├── sql2nosql_tab.py    # Future
    │   │   └── docs_tab.py         # Optional
    │   ├── query_panel.py
    │   ├── sql_panel.py
    │   ├── output_panel.py         # Scrollable, view-only table
    │   └── activity_panel.py       # Structured log renderer
    └── adapters/
        ├── base.py                 # Adapter interface
        ├── text2sql_adapter.py
        └── sql2nosql_adapter.py    # Future

------------------------------------------------------------------------

# 8. Activity Logger API

Every backend stage should emit **structured** events. Prefer rich
`details` over long unstructured messages.

Example:

```python
logger.info(
    stage="schema",
    event="schema_loaded",
    message="Found 24 tables",
    details={"table_count": 24, "duration_ms": 32},
)
logger.info(
    stage="schema",
    event="tables_selected",
    message="Selected relevant tables",
    details={"tables": ["Customers", "Orders"]},
)
logger.info(
    stage="model",
    event="inference_start",
    message="Running Text-to-SQL model",
)
logger.success(
    stage="model",
    event="sql_generated",
    message="SQL generated",
    details={"duration_ms": 462},
)
logger.success(
    stage="validation",
    event="validation_passed",
    message="SQL validation passed",
)
logger.info(
    stage="execution",
    event="executing",
    message="Executing SQL",
)
logger.success(
    stage="execution",
    event="rows_retrieved",
    message="Retrieved 10 rows",
    details={"row_count": 10, "duration_ms": 71},
)
```

------------------------------------------------------------------------

# 9. SQL Safety Rules

Allowed:

-   SELECT
-   WITH (CTE)

Blocked:

-   INSERT
-   UPDATE
-   DELETE
-   DROP
-   ALTER
-   TRUNCATE
-   CREATE

Reject unsafe SQL before execution.

------------------------------------------------------------------------

# 10. Sequence Diagram

    User
     |
     | Enter query + Execute
     v
    UI (Text-to-SQL tab)
     |
     v
    Schema Loader        --> Activity Log (structured)
     |
     v
    Prompt Builder       --> Activity Log
     |
     v
    Fine-tuned Model     --> Activity Log
     |
     v
    SQL Validator        --> Activity Log
     |
     v
    Database Executor    --> Activity Log
     |
     v
    Results (scrollable table, view-only)
     |
     v
    UI

------------------------------------------------------------------------

# 11. Future Enhancements

-   SQL-to-NoSQL tab (MongoDB, DynamoDB, etc.) via adapter interface
-   Documentation tab or in-tab docs per capability
-   Automatic table selection using embeddings
-   SQL / NoSQL explanation panel
-   Query history
-   Multi-database support
-   Conversation memory
-   Authentication
-   Role-based access
-   Streaming token generation

**Out of scope for initial release:** result downloads (CSV/Excel),
charts/dashboards, separate Generate vs Execute buttons.

------------------------------------------------------------------------

# 12. Success Criteria

-   Text-to-SQL workflow works with the fine-tuned model.
-   **Single Execute** button generates SQL, validates, and runs the query.
-   Generated SQL is visible on the same screen after Execute.
-   Only validated read-only SQL executes.
-   Results render in a **scrollable, view-only** table (no download).
-   Activity panel shows **structured, maximally detailed** observable events.
-   Tab shell supports adding **SQL-to-NoSQL** (and documentation) without UI rework.
-   No charts required; table output is sufficient.
-   Entire workflow completes without page refresh.
