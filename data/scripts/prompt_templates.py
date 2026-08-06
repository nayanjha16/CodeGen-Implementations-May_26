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
    "### Write plain-English documentation using the source below.\n"
    "Use the code for context only. In your answer:\n"
    "- Write clear prose for a developer (2-4 short paragraphs)\n"
    "- Describe purpose, behavior, and how it fits the project\n"
    "- Do NOT paste code, signatures, or structure metadata\n"
    "- Do NOT say 'this folder contains' or invent other files\n"
    "### Question:\n{question}\n\n"
    "Repo: {repo_root}\n"
    "Files: {file_list}\n\n"
    "{sources}\n\n"
    "### Documentation:\n"
)

FILE_ASK_INFERENCE_PREFIX = (
    "### Write plain-English documentation for the source file below.\n"
    "Use the code for context only. In your answer:\n"
    "- Write clear prose for a developer (2-4 short paragraphs)\n"
    "- Describe purpose, behavior, and how it fits the project\n"
    "- Do NOT paste code, method signatures, or structure metadata\n"
    "- Do NOT say 'this folder contains', list paths, or mention other files\n"
    "### Question:\n{question}\n\n"
    "Repo: {repo_root}\n"
    "File: {file_name}\n\n"
    "{source}\n\n"
    "### Documentation:\n"
)


def format_folder_ask_inference(
    repo_root: str,
    file_list: str,
    sources: str,
    question: str,
) -> str:
    return FOLDER_ASK_INFERENCE_PREFIX.format(
        repo_root=repo_root.strip(),
        file_list=file_list.strip(),
        sources=sources.strip(),
        question=question.strip(),
    )


def format_file_ask_inference(
    repo_root: str,
    file_name: str,
    source: str,
    question: str,
) -> str:
    return FILE_ASK_INFERENCE_PREFIX.format(
        repo_root=repo_root.strip(),
        file_name=file_name.strip(),
        source=source.strip(),
        question=question.strip(),
    )


def format_code2doc_inference(python_code: str) -> str:
    return CODE2DOC_INFERENCE_PREFIX.format(python_code=python_code.strip())


def format_comment_inference(code_no_comments: str) -> str:
    return COMMENT_INFERENCE_PREFIX.format(code_no_comments=code_no_comments.strip())
