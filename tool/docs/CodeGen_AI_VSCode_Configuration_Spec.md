# CodeGen AI VS Code Configuration Specification

## Purpose

This document describes how the CodeGen AI VS Code extension should be
configured and how it integrates with a Hugging Face OpenAI-compatible
inference endpoint.

------------------------------------------------------------------------

# High-Level Architecture

``` text
VS Code Chat
      │
      ▼
Model Picker
      │
      ▼
CodeGen AI Extension
      │
 ┌────┴───────────────────────┐
 │                            │
 ▼                            ▼
Workspace Services      Language Model Provider
(Indexing/Retrieval)     (Inference)
 │                            │
 └──────────────┬─────────────┘
                ▼
     Hugging Face OpenAI Endpoint
                ▼
      CodeGen Multi Adapter Model
```

The extension owns:

-   Workspace scanning
-   Schema parsing
-   Embedding generation
-   Vector search
-   Intent detection
-   Prompt construction

The Hugging Face endpoint owns:

-   Prompt inference only

------------------------------------------------------------------------

# Configuration Layers

## 1. User Settings (Global)

Stored in VS Code `settings.json`.

These settings are shared across all workspaces.

Example:

``` json
{
  "codegen.endpoint": "https://YOUR-ENDPOINT/v1",
  "codegen.apiKey": "hf_xxxxxxxxx",
  "codegen.model": "codegen-ai",
  "codegen.requestTimeout": 120000,
  "codegen.enableStreaming": true
}
```

  Setting                   Description
  ------------------------- ----------------------------
  codegen.endpoint          OpenAI-compatible endpoint
  codegen.apiKey            Hugging Face API key
  codegen.model             Default remote model
  codegen.requestTimeout    HTTP timeout (ms)
  codegen.enableStreaming   Enable streaming responses

------------------------------------------------------------------------

## 2. Workspace Settings

Stored in:

    .vscode/settings.json

Example:

``` json
{
  "codegen.autoIndex": true,
  "codegen.topK": 3,
  "codegen.embeddingModel": "BAAI/bge-small-en-v1.5",
  "codegen.schemaExtensions": [
    ".sql",
    ".ddl"
  ],
  "codegen.autoReindex": true,
  "codegen.maxSchemaTokens": 6000,
  "codegen.enableIntentDetection": true
}
```

These settings are repository specific.

------------------------------------------------------------------------

## 3. Internal Extension Cache

Stored in:

    .vscode/codegen/

Structure:

    .vscode/
        codegen/
            metadata.json
            index.bin
            config.json
            hashes.json

These files are generated automatically.

Users should never edit them manually.

------------------------------------------------------------------------

# Extension Commands

  Command                       Description
  ----------------------------- -----------------------------
  CodeGen: Scan Workspace       Initial indexing
  CodeGen: Rebuild Index        Full rebuild
  CodeGen: Clear Index          Remove local cache
  CodeGen: Show Statistics      Display index metrics
  CodeGen: Configure Endpoint   Open provider configuration

------------------------------------------------------------------------

# First-Time User Experience

1.  Install the extension.
2.  Open a project.
3.  Select **CodeGen AI** in the Chat model picker (if supported by the
    VS Code AI API used).
4.  Run **CodeGen: Configure Endpoint**.
5.  Enter:
    -   Endpoint URL
    -   API Key
6.  Run **CodeGen: Scan Workspace**.
7.  The extension creates the local semantic index.
8.  Ask questions normally.

------------------------------------------------------------------------

# Chat Request Flow

``` text
User Prompt
      │
      ▼
Intent Detection
      │
      ▼
Embedding Search
      │
      ▼
Retrieve Relevant Schemas
      │
      ▼
Prompt Builder
      │
      ▼
POST /v1/chat/completions
      │
      ▼
Response
```

The endpoint receives only the final prompt.

------------------------------------------------------------------------

# Model Discovery

If the endpoint supports model discovery:

    GET /v1/models

The extension can populate available models dynamically.

Otherwise the configured model name is used.

------------------------------------------------------------------------

# Security

The extension never uploads:

-   Entire repositories
-   Vector indexes
-   Embeddings
-   Local cache

The endpoint receives only:

-   User request
-   Retrieved schemas
-   Generated prompt

------------------------------------------------------------------------

# Acceptance Criteria

A user should be able to:

1.  Install the extension.
2.  Configure a Hugging Face endpoint once.
3.  Open any repository.
4.  Build the local schema index.
5.  Ask natural language questions.
6.  Receive responses without manually supplying schema context.

The experience should resemble using a built-in AI model while keeping
repository awareness entirely inside the extension.
