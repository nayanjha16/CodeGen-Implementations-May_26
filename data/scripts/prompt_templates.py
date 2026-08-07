"""Shared prompt templates for fine-tuning and inference."""

NL2PY_TEMPLATE = (
    "### Instruction: Write Python for: {nl_query}\n"
    "### Response:\n{python_code}"
)

JAVA2PY_TEMPLATE = (
    "### Translate Java to Python:\n"
    "```java\n{java_code}\n```\n"
    "### Python:\n"
    "```python\n{python_code}\n```"
)

NL2PY_INFERENCE_PREFIX = "### Instruction: Write Python for: {nl_query}\n### Response:\n"

NL2JAVA_INFERENCE_PREFIX = (
    "### Instruction: Write Java for: {nl_query}\n"
    "### Response:\n"
    "```java\n"
)

JAVA2PY_INFERENCE_PREFIX = (
    "### Translate Java to Python:\n"
    "```java\n{java_code}\n```\n"
    "### Python:\n"
    "```python\n"
)

RAG_FEW_SHOT_NL2PY = (
    "### Example {idx}:\n"
    "Instruction: Write Python for: {nl_query}\n"
    "Response:\n{python_code}\n\n"
)

RAG_FEW_SHOT_JAVA2PY = (
    "### Example {idx}:\n"
    "Java:\n```java\n{java_code}\n```\n"
    "Python:\n```python\n{python_code}\n```\n\n"
)

RAG_FEW_SHOT_NL2JAVA = (
    "### Example {idx}:\n"
    "Instruction: Write Java for: {nl_query}\n"
    "Response:\n```java\n{java_code}\n```\n\n"
)

CODEGEN_REPO_STYLE = (
    "### Repository style reference ({file_name}):\n"
    "```{lang}\n{snippet}\n```\n\n"
)

CODE2DOC_TEMPLATE = (
    "### Generate documentation for this Python code:\n"
    "```python\n{python_code}\n```\n"
    "### Documentation:\n{documentation}\n"
)

COMMENT_TEMPLATE = (
    "### Add comments to this Python code:\n"
    "```python\n{code_no_comments}\n```\n"
    "### Commented code:\n```python\n{code_with_comments}\n```\n"
)

CODE2DOC_INFERENCE_PREFIX = (
    "### Generate documentation for this Python code:\n"
    "```python\n{python_code}\n```\n"
    "### Documentation:\n"
)

COMMENT_INFERENCE_PREFIX = (
    "### Add comments to this Python code:\n"
    "```python\n{code_no_comments}\n```\n"
    "### Commented code:\n```python\n"
)


def format_nl2py(nl_query: str, python_code: str) -> str:
    return NL2PY_TEMPLATE.format(nl_query=nl_query.strip(), python_code=python_code.strip())


def format_java2py(java_code: str, python_code: str) -> str:
    return JAVA2PY_TEMPLATE.format(java_code=java_code.strip(), python_code=python_code.strip())


def format_nl2py_inference(nl_query: str, few_shot: str = "") -> str:
    prefix = few_shot + NL2PY_INFERENCE_PREFIX.format(nl_query=nl_query.strip())
    return prefix


def format_nl2java_inference(nl_query: str, few_shot: str = "") -> str:
    return few_shot + NL2JAVA_INFERENCE_PREFIX.format(nl_query=nl_query.strip())


def format_codegen_repo_style(file_name: str, lang: str, snippet: str) -> str:
    return CODEGEN_REPO_STYLE.format(
        file_name=file_name.strip(),
        lang=lang.strip(),
        snippet=snippet.strip(),
    )


def format_java2py_inference(java_code: str, few_shot: str = "") -> str:
    prefix = few_shot + JAVA2PY_INFERENCE_PREFIX.format(java_code=java_code.strip())
    return prefix


def format_code2doc(python_code: str, documentation: str) -> str:
    return CODE2DOC_TEMPLATE.format(
        python_code=python_code.strip(),
        documentation=documentation.strip(),
    )


def format_comment(code_no_comments: str, code_with_comments: str) -> str:
    return COMMENT_TEMPLATE.format(
        code_no_comments=code_no_comments.strip(),
        code_with_comments=code_with_comments.strip(),
    )


FOLDER_ASK_INFERENCE_PREFIX = (
    "### Answer the developer's question about this repository.\n\n"
    "User question: {question}\n"
    "What the user is asking: {intent_summary}\n\n"
    "Rules:\n"
    "- Answer ONLY the question above using the source snippets below\n"
    "- Write 2-4 short paragraphs of clear prose for a developer\n"
    "- Ground claims in the snippets; do NOT invent files, APIs, or GitHub metadata\n"
    "- Do NOT repeat these instructions or paste code blocks\n"
    "- Give ONE answer only; do NOT ask follow-up questions\n"
    "- Do NOT simulate a conversation (no Human/User/AI/Assistant turns)\n"
    "{chat_history_section}"
    "Repo: {repo_root}\n"
    "Retrieved sources: {file_list}\n\n"
    "{sources}\n\n"
    "### Answer:\n"
)

REPO_INVENTORY_ASK_INFERENCE_PREFIX = (
    "### Answer the developer's question about this repository.\n\n"
    "User question: {question}\n"
    "What the user is asking: {intent_summary}\n\n"
    "Rules:\n"
    "- Answer ONLY the question above using the information below\n"
    "- Write 2-4 short paragraphs of clear prose for a developer\n"
    "- You MAY list files from the repo inventory when relevant\n"
    "- Distinguish files shown in source snippets from other files in the inventory\n"
    "- Do NOT invent files that are not in the inventory\n"
    "- Give ONE answer only; do NOT ask follow-up questions\n"
    "- Do NOT simulate a conversation (no Human/User/AI/Assistant turns)\n"
    "{chat_history_section}"
    "Repo: {repo_root}\n"
    "Source snippets (retrieved context): {file_list}\n\n"
    "Full repo inventory ({inventory_count} files):\n{repo_inventory}\n\n"
    "{sources}\n\n"
    "### Answer:\n"
)

FILE_ASK_INFERENCE_PREFIX = (
    "### Answer the developer's question about this source file.\n\n"
    "User question: {question}\n"
    "What the user is asking: {intent_summary}\n\n"
    "Rules:\n"
    "- Answer ONLY the question above using the source file below\n"
    "- Write 2-4 short paragraphs of clear prose for a developer\n"
    "- Do NOT paste code blocks or repeat these instructions\n"
    "- Give ONE answer only; do NOT ask follow-up questions\n"
    "- Do NOT simulate a conversation (no Human/User/AI/Assistant turns)\n"
    "Repo: {repo_root}\n"
    "File: {file_name}\n\n"
    "{source}\n\n"
    "### Answer:\n"
)


def _format_chat_history_section(chat_history: str) -> str:
    text = (chat_history or "").strip()
    if not text:
        return ""
    return f"### Recent conversation:\n{text}\n\n"


def format_folder_ask_inference(
    repo_root: str,
    file_list: str,
    sources: str,
    question: str,
    chat_history: str = "",
    intent_summary: str = "",
) -> str:
    return FOLDER_ASK_INFERENCE_PREFIX.format(
        repo_root=repo_root.strip(),
        file_list=file_list.strip(),
        sources=sources.strip(),
        question=question.strip(),
        intent_summary=(intent_summary or question).strip(),
        chat_history_section=_format_chat_history_section(chat_history),
    )


def format_repo_inventory_ask_inference(
    repo_root: str,
    file_list: str,
    sources: str,
    question: str,
    repo_inventory: str,
    inventory_count: int,
    chat_history: str = "",
    intent_summary: str = "",
) -> str:
    return REPO_INVENTORY_ASK_INFERENCE_PREFIX.format(
        repo_root=repo_root.strip(),
        file_list=file_list.strip(),
        sources=sources.strip(),
        question=question.strip(),
        intent_summary=(intent_summary or question).strip(),
        repo_inventory=repo_inventory.strip(),
        inventory_count=inventory_count,
        chat_history_section=_format_chat_history_section(chat_history),
    )


def format_file_ask_inference(
    repo_root: str,
    file_name: str,
    source: str,
    question: str,
    intent_summary: str = "",
) -> str:
    return FILE_ASK_INFERENCE_PREFIX.format(
        repo_root=repo_root.strip(),
        file_name=file_name.strip(),
        source=source.strip(),
        question=question.strip(),
        intent_summary=(intent_summary or question).strip(),
    )


GENERAL_ASK_INFERENCE_PREFIX = (
    "### Answer the developer's question.\n\n"
    "User question: {question}\n\n"
    "Rules:\n"
    "- Answer clearly for a developer using your general programming knowledge\n"
    "- Write 2-4 short paragraphs of clear prose\n"
    "- Do NOT paste code blocks or repeat these instructions\n"
    "- Give ONE answer only; do NOT ask follow-up questions\n"
    "- Do NOT simulate a conversation (no Human/User/AI/Assistant turns)\n"
    "{chat_history_section}"
    "### Answer:\n"
)


def format_general_ask_inference(
    question: str,
    chat_history: str = "",
) -> str:
    return GENERAL_ASK_INFERENCE_PREFIX.format(
        question=question.strip(),
        chat_history_section=_format_chat_history_section(chat_history),
    )


def format_code2doc_inference(python_code: str) -> str:
    return CODE2DOC_INFERENCE_PREFIX.format(python_code=python_code.strip())


def format_comment_inference(code_no_comments: str) -> str:
    return COMMENT_INFERENCE_PREFIX.format(code_no_comments=code_no_comments.strip())


DEBUG_DIAGNOSE_INFERENCE_PREFIX = (
    "### Debug this Python source file.\n"
    "Analyze the problem and respond with:\n"
    "1. **Symptom** — what is going wrong\n"
    "2. **Root cause** — where and why in the code\n"
    "3. **Suggested fix** — concrete change to make\n"
    "4. **Confidence** — high / medium / low\n\n"
    "### Problem report:\n{problem}\n\n"
    "### Validation / runtime evidence:\n{evidence}\n\n"
    "Repo: {repo_root}\n"
    "File: {file_name}\n\n"
    "{source}\n\n"
    "### Diagnosis:\n"
)

DEBUG_FOLLOWUP_INFERENCE_PREFIX = (
    "### Continue debugging this Python source file.\n"
    "Use the prior context and the new question. Respond with a concise, actionable answer.\n\n"
    "### Problem report:\n{problem}\n\n"
    "### Validation / runtime evidence:\n{evidence}\n\n"
    "Repo: {repo_root}\n"
    "File: {file_name}\n\n"
    "{source}\n\n"
    "### Answer:\n"
)


def format_debug_diagnose_inference(
    repo_root: str,
    file_name: str,
    source: str,
    problem: str,
    evidence: str,
) -> str:
    return DEBUG_DIAGNOSE_INFERENCE_PREFIX.format(
        repo_root=repo_root.strip(),
        file_name=file_name.strip(),
        source=source.strip(),
        problem=(problem or "No specific problem described.").strip(),
        evidence=(evidence or "No validation errors detected.").strip(),
    )


def format_debug_followup_inference(
    repo_root: str,
    file_name: str,
    source: str,
    problem: str,
    evidence: str,
) -> str:
    return DEBUG_FOLLOWUP_INFERENCE_PREFIX.format(
        repo_root=repo_root.strip(),
        file_name=file_name.strip(),
        source=source.strip(),
        problem=(problem or "Follow-up question.").strip(),
        evidence=(evidence or "No validation errors detected.").strip(),
    )


def format_debug_fix_context(
    problem: str,
    evidence: str,
    *,
    file_name: str = "",
) -> str:
    parts: list[str] = []
    if problem.strip():
        parts.append(f"User report: {problem.strip()}")
    if file_name.strip():
        parts.append(f"File: {file_name.strip()}")
    if evidence.strip():
        parts.append(f"Evidence:\n{evidence.strip()}")
    return "\n".join(parts) if parts else f"Fix this Python file: {file_name or 'unknown'}"
