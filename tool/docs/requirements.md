# VS Code CodeGen AI Extension - Technical Specification

## Version

v1.0

---

# 1. Overview

## Objective

Build a VS Code extension that allows users to interact with a custom CodeGen Multi-Adapter model exactly like a normal AI coding model.

The extension should automatically:

- Scan the current workspace
- Discover database schemas
- Build and maintain local semantic indexes
- Detect the user's intent
- Retrieve only relevant schemas
- Build the final prompt
- Send the completed prompt to a Hugging Face OpenAI-compatible endpoint
- Display the response inside VS Code Chat

The remote model should remain completely stateless.

The model never scans repositories.

The model only answers the prompt it receives.

---



# 2. Design Principles



## Local First

Everything except inference happens locally.

No schema information leaves the user's machine except the retrieved schema injected into the final prompt.

---



## Stateless Model

The Hugging Face endpoint performs only inference.

It must not:

- maintain repository state
- store embeddings
- scan workspaces
- retrieve schemas

Input:

Complete Prompt

Output:

Model Response

---



## Incremental Indexing

Workspace indexing happens only once.

Subsequent updates should re-index only modified files.

---



## Extensible

Future adapters should be easy to add.

Current adapters:

- text2sql
- sql2nosql
- nosql2doc

Future adapters should require only new PromptBuilders.

---



# 3. High-Level Architecture

User

↓

VS Code Chat

↓

CodeGen Extension

├── Workspace Scanner

├── Schema Parser

├── Embedding Generator

├── Vector Index

├── Intent Detector

├── Schema Retriever

├── Prompt Builder

└── Hugging Face Client

↓

OpenAI Compatible Endpoint

↓

CodeGen Multi Adapter

↓

Response

---



# 4. Repository Structure

```
codegen-extension/

src/

    extension.ts

    commands/

        scanWorkspace.ts

        rebuildIndex.ts

        clearIndex.ts

    scanner/

        workspaceScanner.ts

        schemaScanner.ts

    parser/

        sqlParser.ts

        mongoParser.ts

    embedding/

        embeddingService.ts

        vectorIndex.ts

    retrieval/

        schemaRetriever.ts

    intent/

        intentDetector.ts

    prompt/

        promptBuilder.ts

        templates/

            text2sql.ts

            sql2nosql.ts

            nosql2doc.ts

    provider/

        huggingfaceProvider.ts

    chat/

        codegenChatProvider.ts

    config/

        configuration.ts

resources/

package.json

README.md
```

---



# 5. Supported Schema Types

Initial version

SQL

Supported extensions

- .sql
- .ddl

Future

- Mongo JSON Schema
- Prisma
- Liquibase
- Flyway
- YAML
- GraphQL SDL

---



# 6. Workspace Indexing

Triggered when

- workspace opens
- schema file added
- schema file modified
- manual rebuild

Flow

Workspace

↓

Find schema files

↓

Parse schema

↓

Generate embedding

↓

Store vector

↓

Persist metadata

---



# 7. Schema Parser

Extract

Table Name

Columns

Primary Keys

Foreign Keys

Relationships

Original SQL

Example

Input

CREATE TABLE singer (...)

Output

```
{
 table:"singer",
 columns:[
  "name",
  "country",
  "song_name",
  "age"
 ],
 primaryKey:"singer_id",
 foreignKeys:[],
 schema:"CREATE TABLE..."
}
```

---



# 8. Embedding Engine

Technology

Transformers.js

Recommended model

BAAI/bge-small-en-v1.5

Alternative

all-MiniLM-L6-v2

Generate one embedding per schema.

Future

Generate embeddings per table.

---



# 9. Vector Index

Technology

Use a JavaScript-native ANN library (for example hnswlib-node or another maintained JS vector index implementation).

Each record

```
Embedding

Table Name

Schema

Path

Last Modified

Hash
```

Persist under

```
.vscode/codegen/
```

Files

```
index.bin

metadata.json

config.json
```

---



# 10. Incremental Updates

Each schema stores

SHA256 Hash

Workflow

File Modified

↓

Compute Hash

↓

Hash Changed?

YES

↓

Re-embed

↓

Update Vector

NO

↓

Skip

---



# 11. Intent Detection

Current intents

text2sql

sql2nosql

nosql2doc

Future

sqlExplain

schemaSummary

queryOptimization

Implementation

Rule-based initially.

Future

Small classifier.

---



# 12. Retrieval Pipeline

User Prompt

↓

Generate Query Embedding

↓

Nearest Neighbor Search

↓

Top K Schemas

↓

Return Metadata

Configuration

Default

TopK = 3

Future

Hybrid Ranking

Semantic Similarity

- 

Table Name Match

- 

Foreign Key Connectivity

---



# 13. Prompt Builder

Each adapter owns a template.

Example

Text2SQL

```
Task:
text2sql

Translate the question into SQL.

Schema:

{{schema}}

Question:

{{question}}
```

SQL2NoSQL

```
Task:
sql2nosql

Schema:

{{schema}}

SQL:

{{sql}}
```

NoSQL2Doc

```
Task:
nosql2doc

Schema:

{{schema}}

Query:

{{query}}
```

---



# 14. Hugging Face Client

Endpoint

```
POST

/v1/chat/completions
```

Payload

```
{
 model:"codegen-multi-adapter",

 messages:[
   {
      role:"user",
      content:"FULL PROMPT"
   }
 ]
}
```

No repository context.

No embeddings.

No workspace metadata.

Only final prompt.

---



# 15. Configuration

Extension Settings

```
codegen.endpoint

codegen.apiKey

codegen.model

codegen.autoIndex

codegen.topK

codegen.embeddingModel

codegen.schemaExtensions

codegen.maxPromptTokens
```

---



# 16. VS Code Integration

Register

Commands

```
CodeGen: Scan Workspace

CodeGen: Rebuild Index

CodeGen: Clear Index
```

Register

Chat Provider

or

Language Model Provider (preferred if supported by the target VS Code API).

---



# 17. Local Cache

Store under

```
.vscode/codegen/
```

```
metadata.json

index.bin

config.json

cache/
```

Never upload cache.

---



# 18. Logging

Provide

Info

Debug

Error

Performance

Log

Workspace indexed

Schemas found

Embedding time

Retrieval time

Inference time

---



# 19. Error Handling

Missing API Key

Missing Endpoint

Workspace Empty

No Schema Found

Embedding Failure

HTTP Failure

Inference Timeout

Show actionable VS Code notifications.

---



# 20. Performance Targets

Workspace Scan

< 2 seconds

Embedding Generation

< 100 ms per schema

Retrieval

< 20 ms

Prompt Construction

< 5 ms

Remote Inference

Dependent on endpoint

---



# 21. Security

Never upload entire repository.

Only upload:

Retrieved schema

User prompt

Task type

No telemetry by default.

No persistent cloud storage.

---



# 22. Future Enhancements

Hybrid Retrieval

Relationship Graph Search

Cross-file Schema Linking

Prompt Compression

Automatic SQL Validation

Execute SQL Tool

Result Explanation

Multi-step Agent Workflow

Adapter Marketplace

---



# 23. Milestone Plan



## Milestone 1

- Extension scaffold
- Configuration
- Workspace access
- Commands

Deliverable:
Workspace scanning works.

---



## Milestone 2

- SQL parser
- Metadata extraction
- JSON persistence

Deliverable:
Schema catalog.

---



## Milestone 3

- Embedding generation
- Local vector index
- Incremental indexing

Deliverable:
Semantic schema search.

---



## Milestone 4

- Intent detection
- Schema retrieval
- Prompt builder

Deliverable:
Automatically constructed prompts.

---



## Milestone 5

- Hugging Face OpenAI client
- Streaming responses
- Error handling

Deliverable:
End-to-end inference.

---



## Milestone 6

- VS Code Chat integration
- Settings UI
- Progress notifications
- Workspace watchers

Deliverable:
Production-ready extension.

---



# 24. Acceptance Criteria

The following workflow must work without manual prompt engineering.

User types:

"How many singers do we have?"

The extension automatically:

1. Detects the intent as `text2sql`.
2. Searches the indexed schemas.
3. Selects the relevant `singer` table.
4. Constructs the complete prompt expected by the CodeGen model.
5. Sends the prompt to the Hugging Face OpenAI-compatible endpoint.
6. Streams the generated SQL response back into the VS Code chat interface.

The user never manually pastes schemas, chooses tables, or constructs prompts.

The experience should feel equivalent to using a built-in AI coding model, while all repository-specific intelligence remains inside the extension and the remote model stays stateless.