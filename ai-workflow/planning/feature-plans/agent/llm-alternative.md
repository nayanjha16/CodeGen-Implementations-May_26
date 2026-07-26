# Orchestrator LLM — GPT-5 Replacement

> **Spec reference:** `agent.md` §14 lists “GPT-5.5 (or compatible model with **tool calling**)”.  
> **Constraint:** No OpenAI / large cloud models — local machine only.

The orchestrator LLM does **orchestration**, not SQL generation:

| Task | Orchestrator LLM | CodeGen + LoRA (Cloud Run) |
| --- | --- | --- |
| Detect user intent (text2sql vs mongo vs doc vs explain) | ✅ | ❌ |
| Choose tool sequence | ✅ | ❌ |
| Summarize query results (FR-6) | ✅ | ❌ |
| Explain existing SQL in plain language | ✅ | ❌ |
| Generate SQL / Mongo / documentation | ❌ | ✅ |

---

## Recommended options (best → lightest)

### Option A — Qwen 2.5 7B Instruct (recommended if RAM ≥ 16 GB)

```bash
ollama pull qwen2.5:7b-instruct
```

| Pros | Cons |
| --- | --- |
| Strong structured JSON / tool-style outputs | ~4–8 GB RAM |
| Good intent classification | Slower than 4B on CPU |
| Works with LangGraph + `langchain-ollama` | |

**Use for:** intent detection, planning, FR-6 summary, explain SQL.

---

### Option B — Gemma 3 4B (you already have this)

```bash
ollama pull gemma3:4b
```

| Pros | Cons |
| --- | --- |
| Already installed for eval judge | Weaker multi-step tool planning |
| Fast on CPU | May need stricter JSON prompts |
| Low RAM | |

**Use for:** same roles as Option A; add **explicit JSON schema** in prompts and fallback rules when parse fails.

---

### Option C — Llama 3.2 3B

```bash
ollama pull llama3.2:3b
```

Lighter than Qwen 7B; better than Gemma for some instruction tasks. Middle ground if 7B is too slow.

---

### Option D — Hybrid (most reliable on weak hardware)

| Step | Engine |
| --- | --- |
| Intent | Keyword rules first (same patterns as `codegen_api` classifier) |
| Ambiguous intent | Ollama gemma3:4b single-shot JSON `{ "intent": "..." }` |
| Planning | **Deterministic** `planner.py` map intent → tool list |
| Summary / explain | Ollama gemma3:4b |

LangGraph still runs the graph; LLM is not free-form planning every step.

---

## How LangGraph uses Ollama (not GPT)

```text
┌─────────────────────────────────────────┐
│  Ollama (orchestrator)                   │
│  • System: agent.md §11 prompt           │
│  • Tools bound: schema, fastapi, execute │
│  • Model picks tool OR planner is fixed  │
└───────────────┬─────────────────────────┘
                │ tool calls
                ▼
┌─────────────────────────────────────────┐
│  Three MCP-compatible Python tools       │
└───────────────┬─────────────────────────┘
                │ generate_sql / nosql / doc
                ▼
┌─────────────────────────────────────────┐
│  Cloud Run CodeGen /v1/chat/completions  │
│  intent + LoRA adapters                  │
└─────────────────────────────────────────┘
```

**Libraries:** `langgraph`, `langchain-ollama` (or raw `httpx` to `OLLAMA_BASE_URL/api/chat`).

**Config (`agent/.env`):**

```bash
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_ORCHESTRATOR_MODEL=qwen2.5:7b-instruct   # or gemma3:4b
OLLAMA_TIMEOUT=120
```

Separate from judge model — can be the same tag if you only want one Ollama model loaded.

---

## Capability matrix by model

| Requirement | gemma3:4b | qwen2.5:7b | Hybrid D |
| --- | --- | --- | --- |
| FR-1 intent | ⚠️ OK with rules backup | ✅ | ✅ |
| FR-6 summary | ✅ | ✅ | ✅ |
| Explain SQL | ✅ | ✅ | ✅ |
| Tool calling via LangGraph | ⚠️ | ✅ | ✅ (rules + LLM) |
| Runs on your CPU setup | ✅ | ⚠️ slower | ✅ |

---

## Recommendation for your capstone write-up

> We replaced GPT-5.5 with a **local Ollama orchestrator** (Qwen 2.5 7B or Gemma 3 4B) for intent, planning support, and natural-language responses. **SQL and NoSQL generation remain delegated** to the fine-tuned CodeGen-350M LoRA adapters via the Capstone FastAPI service, preserving the agent.md principle that the agent never generates queries directly.

---

## Not recommended

| Model | Why |
| --- | --- |
| GPT-4 / GPT-5 | User system constraint |
| CodeGen as orchestrator | Wrong model — it generates SQL, not tool routing |
| No LLM at all | Hard to satisfy FR-6 and “explain SQL” convincingly for capstone demo |

---

## Your machine — can you use Qwen 2.5 7B after eval?

**Target hardware:** i5-1245U, **24 GB RAM**, Intel Iris Xe (no NVIDIA GPU).

| Question | Answer |
| --- | --- |
| Enough RAM for 7B? | **Yes** — with Q4 quantization (~5–6 GB model + ~2 GB context) |
| Enough for eval + 7B + Docker at once? | **Tight** — finish long CPU eval first, then pull 7B |
| GPU acceleration? | **No CUDA** — orchestrator runs on **CPU** (slow but OK for demo) |
| Decide after eval? | **Yes** — sensible; compare gemma3:4b vs qwen after baseline/lora complete |

### Two ways to load Qwen (both cache locally)

| Approach | Cache location | Best for |
| --- | --- | --- |
| **Ollama** (recommended) | `%USERPROFILE%\.ollama\models` | Agent orchestrator — same as gemma3:4b today |
| **Hugging Face + transformers** | `%USERPROFILE%\.cache\huggingface` | If you want `from_pretrained` in Python directly |

**Recommendation:** Use **Ollama** for the agent orchestrator even if eval uses HF elsewhere. One command, automatic quantize, works with LangGraph:

```powershell
ollama pull qwen2.5:7b-instruct
ollama run qwen2.5:7b-instruct "Reply OK if you can hear me."
```

Agent config:

```bash
OLLAMA_ORCHESTRATOR_MODEL=qwen2.5:7b-instruct
```

### HF direct load (optional — only if you skip Ollama)

```python
# 4-bit on CPU — fits 24 GB but slow; cache under ~/.cache/huggingface
from transformers import AutoModelForCausalLM, AutoTokenizer
model = AutoModelForCausalLM.from_pretrained(
    "Qwen/Qwen2.5-7B-Instruct",
    device_map="cpu",
    load_in_4bit=True,  # needs bitsandbytes
)
```

More setup, no benefit over Ollama for this capstone unless you have a specific reason.

### Practical workflow after eval

1. Finish baseline + LoRA gold eval (local CodeGen on CPU — heavy).
2. `ollama pull qwen2.5:7b-instruct` (or keep gemma3:4b if 7B too slow on first test).
3. Build agent — CodeGen inference via **Cloud Run** (not local), so RAM goes to Ollama + Docker only.
4. If 7B feels too slow (~10–30 s per orchestrator turn on i5-1245U), fall back to **gemma3:4b** or **hybrid rules + gemma**.

### RAM budget (agent phase, after eval)

| Component | Approx RAM |
| --- | --- |
| Windows + background | ~4–6 GB |
| TEND Docker (Postgres + Mongo) | ~1–2 GB |
| Ollama qwen2.5:7b (Q4) | ~5–6 GB |
| Agent Python process | ~0.5 GB |
| **Total** | ~12–15 GB — **fits in 24 GB** |

CodeGen generation stays on **Cloud Run** — no local 350M model needed during agent work.
