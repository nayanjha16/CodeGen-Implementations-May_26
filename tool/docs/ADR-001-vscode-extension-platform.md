# ADR-001: Deliver CodeGen AI as a VS Code Extension

| Field | Value |
| --- | --- |
| Status | Accepted |
| Date | 2026-07-15 |
| Deciders | CodeGen AI product / engineering |
| Related docs | [requirements.md](./requirements.md), [CodeGen_AI_VSCode_Configuration_Spec.md](./CodeGen_AI_VSCode_Configuration_Spec.md) |

---

## Context

CodeGen AI needs an in-editor experience where users ask natural-language questions over local database schemas and receive adapter-specific answers (for example text2sql) **without** manually pasting schemas or crafting prompts.

The intended architecture is:

1. Extension owns workspace scanning, schema parsing, embeddings, vector search, intent detection, and prompt construction.
2. A Hugging Face OpenAI-compatible endpoint owns **inference only**.
3. The endpoint receives the final assembled prompt — not the whole repository, vector index, or embeddings.
4. The user experience should feel like selecting a built-in chat model (appear in the Chat model picker / Chat UI, stream responses).

We evaluated three delivery surfaces:

- **VS Code extension** (Language Model Chat Provider / Chat integration)
- **Cursor extension** (same extension model, but targeting Cursor’s chat stack)
- **Cursor Agent** (rules, skills, MCP, and/or BYOK custom model)

---

## Decision

**We will implement CodeGen AI as a Visual Studio Code extension**, using the VS Code Chat / Language Model Chat Provider APIs for the primary user experience.

Cursor is deferred as a secondary surface at most (for example MCP tools later). It is **not** the primary product platform for this release.

---

## Options Considered

### Option A — VS Code Extension (chosen)

Build an extension that:

- Registers commands (`Scan Workspace`, `Rebuild Index`, `Clear Index`, configure endpoint)
- Maintains a local semantic index under `.vscode/codegen/`
- Registers a Language Model Chat Provider (preferred) or Chat Participant so **CodeGen AI** appears in VS Code Chat
- On each chat request: intent → retrieve schemas → build adapter prompt → `POST /v1/chat/completions` → stream response

**Pros**

- Matches the published requirements and acceptance criteria exactly
- First-class Chat / Language Model Provider APIs for contributing a custom model
- Full control over the request path: only the final CodeGen prompt leaves the machine
- Standard extension lifecycle: settings, commands, workspace FS, progress notifications
- Aligns with local-first and stateless-model design principles

**Cons**

- Separate install from Cursor (Cursor users do not get this UX by default)
- Requires maintaining a VS Code extension package and Chat API compatibility

### Option B — Cursor Extension mirroring VS Code Chat

Ship a similar extension targeting Cursor’s editor (VS Code fork) and Cursor Chat.

**Pros**

- Cursor is popular for AI coding
- Non-chat pieces (commands, settings, local index) can largely reuse VS Code extension APIs

**Cons**

- Cursor does **not** support the VS Code Chat Participant API for third-party extensions (confirmed gaps; extensions that register chat participants can fail or get incomplete APIs)
- Cursor does **not** expose native models via `vscode.lm`, and Language Model tool registration (`vscode.lm.registerTool`) is not supported
- Cursor’s Chat / Agent UI is proprietary; contributing “CodeGen AI” to Cursor’s model picker via VS Code LM Chat Provider is not a supported product path
- Risk of building against incomplete APIs and shipping a broken or unsupported Chat experience

**Rejected** for the primary Chat UX. Reusing extension libraries for indexing in Cursor later remains possible, but Chat integration must not depend on unsupported Cursor APIs.

### Option C — Cursor Agent (rules / skills / MCP / BYOK)

Approximate the product with Cursor Agent:

- BYOK OpenAI-compatible Hugging Face endpoint in Cursor Settings → Models
- Rules/skills instructing the agent how to call CodeGen
- MCP tools for schema search / prompt assembly

**Pros**

- Faster experiment on Cursor without a Chat Provider
- MCP is a Cursor-supported extension point (`mcp.json` / `vscode.cursor.mcp.registerServer`)
- Indexing logic could live in an MCP server shared later

**Cons**

- Agent retains control of tool use and prompt shape; retrieval and adapter templates are **not guaranteed**
- Does not appear as a dedicated CodeGen model with a deterministic pipeline
- Custom endpoints are limited in Cursor Agent/Composer; chat/plan routing may not match the extension’s controlled inference path
- Violates the core principle that the remote model stays stateless and receives **only** the extension-built prompt
- Weaker match to acceptance criteria (“feels equivalent to a built-in AI coding model” with automatic schema injection)

**Rejected** as the primary delivery for this product. MCP may be revisited later as an optional Cursor sidecar.

---

## Decision Drivers

| Driver | Why it matters | Winner |
| --- | --- | --- |
| Chat UX with selectable CodeGen model | Spec requires model-picker / chat integration | VS Code |
| Owned prompt pipeline (intent → retrieve → template) | Product differentiation and adapter correctness | VS Code |
| Stateless remote inference | Security and architecture (HF sees final prompt only) | VS Code |
| Local-first indexing | Schemas stay on machine except retrieved snippets | VS Code (or MCP later) |
| Supported public APIs | Ship on a stable extension surface | VS Code |
| Cursor Agent convenience | Speed of experiment, not product fidelity | Cursor Agent (secondary only) |

---

## Consequences

### Positive

- Implementation can follow [requirements.md](./requirements.md) milestones without platform workarounds
- Acceptance criteria are testable end-to-end in VS Code Chat
- Security story stays clear: index/embeddings never uploaded; endpoint receives prompt + retrieved schemas only
- Future adapters remain prompt-builder changes inside the extension

### Negative / follow-ups

- Cursor users will not get the same first-class Chat experience in this release
- If Cursor later supports Language Model Chat Provider / Chat Participant APIs properly, reassess dual packaging
- Optional later work: expose retrieve/prompt tools via MCP for Cursor Agent without replacing the VS Code extension as primary

### Out of scope for this decision

- Hugging Face endpoint topology and model training
- Choice of embedding/vector libraries (see requirements)
- Publishing channel (Marketplace vs private VSIX) — separate decision

---

## Validation Against Acceptance Criteria

From [requirements.md](./requirements.md) §24, the user must type a natural question and get automatic text2sql (or other adapter) behavior with streaming chat output.

| Criterion | VS Code extension | Cursor extension (Chat) | Cursor Agent |
| --- | --- | --- | --- |
| Install once, configure HF endpoint | Yes | Partial | Yes (BYOK) |
| Build local schema index | Yes | Yes (non-chat APIs) | Possible via MCP |
| Ask NL questions without pasting schemas | Yes | Not reliably | Best-effort |
| CodeGen appears in Chat / model picker | Yes | No | No |
| Deterministic intent + retrieval + prompt | Yes | No | No |
| Endpoint receives only final prompt | Yes | N/A | No guarantee |

---

## References

- Internal: [requirements.md](./requirements.md), [CodeGen_AI_VSCode_Configuration_Spec.md](./CodeGen_AI_VSCode_Configuration_Spec.md)
- [VS Code Language Model Chat Provider API](https://code.visualstudio.com/api/extension-guides/ai/language-model-chat-provider)
- [VS Code Chat Participant API](https://code.visualstudio.com/api/extension-guides/ai/chat)
- [Cursor Extension API](https://cursor.com/docs/extension-api) (MCP / plugins only; not VS Code Chat Provider)
- Cursor forum: incomplete / missing VS Code LM and Chat Participant support for third-party extensions

---

## Revision History

| Date | Change |
| --- | --- |
| 2026-07-15 | Initial decision: VS Code extension as primary platform |
