# AI Database Agent Platform

## Functional & Technical Specification

**Version:** 1.0
**Project:** AI Database Agent with MCP Tool Calling
**Author:**  K.Bhavani
**Purpose:** IIIT Hyderabad AIML Capstone Project

---

# 1. Overview

## Objective

Build an AI Agent capable of answering natural language database questions by orchestrating multiple tools instead of generating SQL directly.

The system will:

* Understand user intent
* Retrieve only the required database schema
* Invoke the Cloud Run CodeGen API (LoRA v3 via `/v1/chat/completions`)
* Execute generated queries
* Return results in natural language
* Retry automatically when execution fails

The architecture demonstrates modern Agentic AI concepts including:

* AI Agents
* MCP Tool Calling
* Tool Orchestration
* Fine-tuned LLM
* Database Execution
* Self-correction loop

---

# 2. High Level Architecture

```
                     User
                       │
                       ▼
             ┌──────────────────────┐
             │      AI Agent        │
             │                      │
             │ Intent Detection     │
             │ Planning             │
             │ Tool Selection       │
             │ Memory               │
             └──────────┬───────────┘
                        │
      ─────────────────────────────────────────
      │                 │                     │
      ▼                 ▼                     ▼

┌──────────────┐  ┌─────────────────┐  ┌────────────────┐
│Schema Tool   │  │ CodeGen API     │  │ Execution Tool │
│              │  │ (FastAPI)       │  │                │
│Schema Search │  │ Text→SQL        │  │ Execute SQL    │
│Metadata      │  │ SQL→NoSQL       │  │ Execute Mongo  │
│Relationships │  │ SQL→Docs        │  │ Return Results │
└──────────────┘  └─────────────────┘  └────────────────┘
```

---

# 3. Goals

The project demonstrates:

* Agentic AI
* MCP architecture
* Tool calling
* Fine-tuned models
* Database interaction
* Error recovery
* Production-ready architecture

---

# 4. Functional Requirements

## FR-1 User Query

Input

```
Show top 10 customers by revenue.
```

Agent determines

```
Intent:
Text2SQL
```

---

## FR-2 Schema Extraction

Instead of sending the entire database schema,

Agent calls

```
Schema Tool
```

Example response

```json
{
  "tables": [
    "customers",
    "orders",
    "payments"
  ],
  "relationships": [
    ...
  ],
  "columns": [
    ...
  ]
}
```

---

## FR-3 Query Generation

Agent calls

```
FastAPI
```

Example

```http
POST /generate/sql
```

Input

```json
{
    "question":"Top customers",
    "schema":{}
}
```

Output

```sql
SELECT ...
```

---

## FR-4 Query Execution

Agent invokes

```
Execution Tool
```

Returns

```json
{
   "rows":[]
}
```

---

## FR-5 Error Recovery

If SQL execution fails

```
SQL

↓

Database Error

↓

Agent

↓

FastAPI

↓

Corrected SQL

↓

Execute Again
```

Maximum retries

```
3
```

---

## FR-6 Natural Language Response

Agent summarizes results.

Example

```
Top customer is ABC Corp with total revenue ₹15.2M.
```

---

# 5. Supported Capabilities

## Text → SQL

```
Question

↓

SQL
```

---

## SQL → MongoDB

```
SQL

↓

Mongo Aggregation
```

---

## SQL Documentation

```
SQL

↓

Business Explanation
```

---

## Explain SQL

```
SQL

↓

Step-by-step explanation
```

---

## Query Validation

Validate

* syntax
* missing tables
* missing joins
* unsafe queries

---

# 6. AI Agent Responsibilities

The agent NEVER generates SQL.

Responsibilities

* Intent detection
* Planning
* Tool selection
* Tool orchestration
* Retry
* Response formatting

---

# 7. MCP Tools

## Tool 1

Schema Extraction Tool

Purpose

Return only relevant schema.

Input

```json
{
    "question":"..."
}
```

Output

```json
{
    "tables":[],
    "columns":[],
    "relationships":[]
}
```

---

## Tool 2

CodeGen API client (`agent/clients/codegen_client.py`)

Purpose

Generate SQL, MongoDB queries, or documentation via the deployed multi-adapter API.

Endpoint (production)

```
POST /v1/chat/completions
```

OpenAI-compatible body with schema in the user message; optional `"intent": "text2sql" | "sql2nosql" | "nosql2doc"`.

---

## Tool 3

Execution Tool

Purpose

Execute SQL

Input

```json
{
   "query":"..."
}
```

Output

```json
{
   "rows":[]
}
```

---

# 8. Agent Workflow

```
User

↓

Understand Intent

↓

Need Schema?

↓

Call Schema Tool

↓

Need Query?

↓

Call FastAPI

↓

Need Execution?

↓

Call Execution Tool

↓

Error?

↓

Retry

↓

Summarize

↓

Return Response
```

---

# 9. Sequence Diagram

```
User
 │
 │ Question
 ▼

Agent
 │
 │ Extract Schema
 ▼

Schema Tool
 │
 │ Relevant Tables
 ▼

Agent
 │
 │ Generate SQL
 ▼

FastAPI
 │
 │ SQL
 ▼

Agent
 │
 │ Execute
 ▼

Execution Tool
 │
 │ Results
 ▼

Agent
 │
 │ Summary
 ▼

User
```

---

# 10. FastAPI Endpoints

> **Deployed API (`fastapi-deploy/codegen_api`):** OpenAI-compatible **`POST /v1/chat/completions`** only — not the convenience routes below. The agent maps spec intents via `agent/tools/fastapi_tool.py` (e.g. `intent: "text2sql"`). SQL **explanation** uses the local Ollama orchestrator, not CodeGen. See [fastapi-deploy/README.md](../../fastapi-deploy/README.md).

## Generate SQL

```
POST

/generate/sql
```

---

## SQL to Mongo

```
POST

/generate/nosql
```

---

## SQL Documentation

```
POST

/generate/documentation
```

---

## SQL Explanation

```
POST

/generate/explanation
```

---

## Health

```
GET

/health
```

---

# 11. Agent Prompt

```
You are an AI Database Agent.

Never generate SQL directly.

Always use tools.

Workflow

1. Detect intent.

2. Retrieve relevant schema.

3. Call the CodeGen API (Cloud Run `/v1/chat/completions`).

4. Execute generated query if requested.

5. If execution fails, retry by passing the error back to the model.

6. Return natural language results.

Never assume table names.

Never hallucinate schemas.
```

---

# 12. Project Structure

```
agent/                          # AI Database Agent (this repo)
├── main.py                     # CLI
├── web/                        # FastAPI chat UI
├── orchestration/              # LangGraph pipeline
├── orchestrator/               # Intent, planner, prompts, retry
├── tools/                      # schema_tool, codegen client, execution_tool
├── mcp/                        # stdio MCP server
├── database/                   # Postgres + Mongo profiles
├── scripts/                    # verify DBs, run_capstone_demo.py
├── data/standalone/            # Chinook / Northwind demo SQL
└── tests/

fastapi-deploy/                 # Cloud Run serving package (separate)
└── codegen_api/                # OpenAI-compatible API + PEFT hot-swap
    ├── api/app.py
    ├── adapters/               # LoRA router
    └── classifier/
```

---

# 13. Future Enhancements

### Phase 2

* Multi-database support
* PostgreSQL
* MySQL
* Oracle
* SQL Server
* MongoDB
* Snowflake

---

### Phase 3

Schema embedding search

Instead of querying metadata each time,

Store

```
Table descriptions

Relationships

Column descriptions

Examples
```

inside a Vector Database.

---

### Phase 4

Conversation Memory

Example

```
User

Show top customers.

↓

Now only from Hyderabad.

↓

Now sort descending.
```

The agent remembers previous context.

---

### Phase 5

Human Approval

Before executing

```
Generated SQL

↓

Preview

↓

Approve

↓

Execute
```

---

### Phase 6

Query Optimization

Analyze

* indexes
* execution plan
* estimated cost

Recommend better SQL.

---

# 14. Technology Stack

| Component             | Technology                                           |
| --------------------- | ---------------------------------------------------- |
| Agent Framework       | LangGraph (preferred) or OpenAI Agents SDK           |
| LLM                   | GPT-5.5 (or compatible model with tool calling)      |
| Tool Protocol         | Model Context Protocol (MCP)                         |
| API Framework         | FastAPI                                              |
| Fine-tuned Models     | Your Text→SQL, SQL→NoSQL, SQL→Documentation adapters |
| Databases             | PostgreSQL, MongoDB                                  |
| ORM/DB Access         | SQLAlchemy + PyMongo                                 |
| Vector Store (Future) | FAISS or Chroma                                      |
| Authentication        | API Keys / OAuth (future)                            |
| Deployment            | Docker, Hugging Face (API), or AWS EC2/ECS           |
| Monitoring            | LangSmith / OpenTelemetry (optional)                 |

---

# 15. Capstone Value Proposition

This project goes beyond a traditional Text-to-SQL application by demonstrating a complete **Agentic AI workflow**. The AI agent acts as an orchestrator, intelligently selecting MCP-compatible tools to retrieve relevant schema, invoke specialized fine-tuned models through FastAPI, execute generated SQL or NoSQL queries, recover automatically from execution errors, and present results in natural language. The modular architecture enables each capability to evolve independently while showcasing modern AI engineering practices such as tool calling, self-correction, and extensibility. This design aligns with current enterprise trends in AI-powered data assistants and provides a strong foundation for future enhancements including vector-based schema retrieval, multi-database support, conversation memory, human approval workflows, and query optimization.
