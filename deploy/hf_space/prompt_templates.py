"""Shared prompt templates for fine-tuning and inference."""

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

CODE2DOC_INFERENCE_PREFIX = (
    "### Generate documentation for this Python code:\n"
    "```python\n{python_code}\n```\n"
    "### Documentation:\n"
)


def format_nl2py_inference(nl_query: str, few_shot: str = "") -> str:
    return few_shot + NL2PY_INFERENCE_PREFIX.format(nl_query=nl_query.strip())


def format_nl2java_inference(nl_query: str, few_shot: str = "") -> str:
    return few_shot + NL2JAVA_INFERENCE_PREFIX.format(nl_query=nl_query.strip())


def format_java2py_inference(java_code: str, few_shot: str = "") -> str:
    return few_shot + JAVA2PY_INFERENCE_PREFIX.format(java_code=java_code.strip())


def format_code2doc_inference(python_code: str) -> str:
    return CODE2DOC_INFERENCE_PREFIX.format(python_code=python_code.strip())
