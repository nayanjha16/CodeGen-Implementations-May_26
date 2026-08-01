"""Curated, shared showcase inputs for Gradio and FastAPI.

Every repository/task pair exposes at least three non-empty examples. Code
inputs are deliberately small and structurally valid so the UI demonstrates
model behaviour rather than malformed showcase data. Generation remains
model-driven: the catalogue never substitutes a reference answer for a model
completion.
"""

from __future__ import annotations

import ast
import re
from collections import Counter
from pathlib import Path
from typing import Any, Dict, List, Optional

from src.config import CONFIG
from src.repository_catalog import repository_path


TASK_IO = {
    "T1": ("Natural Language", "Python"),
    "T2": ("Natural Language", "Java"),
    "T3": ("Python", "Java"),
    "T4": ("Java", "Python"),
    "T5": ("Python", "Natural Language"),
    "T6": ("Java", "Natural Language"),
}

REPOSITORY_IDS = ("generic", "ledgerflow", "aws_s3")
MINIMUM_EXAMPLES_PER_SECTION = 3

PYTHON_GENERATION_SUFFIX = (
    " Return only syntactically valid multi-line Python code. Put imports and "
    "the function definition on separate lines. Do not use Markdown fences."
)
JAVA_GENERATION_SUFFIX = (
    " Return one complete, compilable Java class only. Do not use Markdown "
    "fences or add an explanation."
)


def _row(
    showcase_id: str,
    repository_id: str,
    title: str,
    task_id: str,
    input_text: str,
    *,
    use_rag: bool,
    description: str,
    expected_sources: Optional[List[str]] = None,
    source_path: Optional[str] = None,
) -> Dict[str, Any]:
    source, target = TASK_IO[task_id]
    return {
        "showcase_id": showcase_id,
        "repository_id": repository_id,
        "title": title,
        "task_id": task_id,
        "source_language": source,
        "target_language": target,
        "use_rag": use_rag,
        "capability": f"{source} -> {target}",
        "description": description,
        "expected_sources": list(expected_sources or []),
        "source_path": source_path,
        "input_text": input_text.strip(),
    }


def _generic_examples() -> List[Dict[str, Any]]:
    description = "A small standalone example with no repository claim."
    return [
        # T1: Natural Language -> Python
        _row(
            "generic_t1_clamp", "generic", "Clamp a number", "T1",
            "Implement clamp(value, minimum, maximum). Return minimum when value "
            "is smaller, maximum when value is larger, and value otherwise."
            + PYTHON_GENERATION_SUFFIX,
            use_rag=False, description=description,
        ),
        _row(
            "generic_t1_simple_interest", "generic", "Calculate simple interest", "T1",
            "Implement calculate_simple_interest(principal, annual_rate, years) "
            "using principal * annual_rate * years / 100.0."
            + PYTHON_GENERATION_SUFFIX,
            use_rag=False, description=description,
        ),
        _row(
            "generic_t1_even", "generic", "Check an even integer", "T1",
            "Implement is_even(value: int) -> bool using the remainder operator."
            + PYTHON_GENERATION_SUFFIX,
            use_rag=False, description=description,
        ),

        # T2: Natural Language -> Java
        _row(
            "generic_t2_clamp", "generic", "Java integer clamp", "T2",
            "Implement public class NumberUtils with public static int clamp(int "
            "value, int minimum, int maximum)." + JAVA_GENERATION_SUFFIX,
            use_rag=False, description=description,
        ),
        _row(
            "generic_t2_temperature", "generic", "Java temperature conversion", "T2",
            "Implement public class TemperatureConverter with public static double "
            "celsiusToFahrenheit(double value), returning value * 9.0 / 5.0 + 32.0."
            + JAVA_GENERATION_SUFFIX,
            use_rag=False, description=description,
        ),
        _row(
            "generic_t2_discount", "generic", "Java discount calculator", "T2",
            "Implement public class DiscountCalculator with public static double "
            "finalPrice(double price, double discountPercent)."
            + JAVA_GENERATION_SUFFIX,
            use_rag=False, description=description,
        ),

        # T3: Python -> Java
        _row(
            "generic_t3_temperature", "generic", "Translate temperature conversion", "T3",
            "def celsius_to_fahrenheit(value: float) -> float:\n"
            "    return value * 9.0 / 5.0 + 32.0",
            use_rag=False, description=description,
        ),
        _row(
            "generic_t3_clamp", "generic", "Translate Python clamp", "T3",
            "def clamp(value: int, minimum: int, maximum: int) -> int:\n"
            "    return max(minimum, min(value, maximum))",
            use_rag=False, description=description,
        ),
        _row(
            "generic_t3_positive_count", "generic", "Translate positive counter", "T3",
            "def count_positive(values: list[int]) -> int:\n"
            "    return sum(1 for value in values if value > 0)",
            use_rag=False, description=description,
        ),

        # T4: Java -> Python
        _row(
            "generic_t4_clamp", "generic", "Translate Java clamp", "T4",
            "public static int clamp(int value, int minimum, int maximum) {\n"
            "    return Math.max(minimum, Math.min(value, maximum));\n}",
            use_rag=False, description=description,
        ),
        _row(
            "generic_t4_even", "generic", "Translate Java even check", "T4",
            "public static boolean isEven(int value) {\n"
            "    return value % 2 == 0;\n}",
            use_rag=False, description=description,
        ),
        _row(
            "generic_t4_maximum", "generic", "Translate maximum of three", "T4",
            "public static int maximum(int first, int second, int third) {\n"
            "    return Math.max(first, Math.max(second, third));\n}",
            use_rag=False, description=description,
        ),

        # T5: Python -> Natural Language
        _row(
            "generic_t5_group", "generic", "Explain Python grouping", "T5",
            "def group_by_department(employees):\n"
            "    grouped = {}\n"
            "    for employee in employees:\n"
            "        grouped.setdefault(employee['department'], []).append(employee)\n"
            "    return grouped",
            use_rag=False, description=description,
        ),
        _row(
            "generic_t5_running_total", "generic", "Explain a running total", "T5",
            "def running_total(values):\n"
            "    total = 0\n"
            "    result = []\n"
            "    for value in values:\n"
            "        total += value\n"
            "        result.append(total)\n"
            "    return result",
            use_rag=False, description=description,
        ),
        _row(
            "generic_t5_unique", "generic", "Explain stable deduplication", "T5",
            "def unique_in_order(values):\n"
            "    seen = set()\n"
            "    return [value for value in values if not (value in seen or seen.add(value))]",
            use_rag=False, description=description,
        ),

        # T6: Java -> Natural Language
        _row(
            "generic_t6_clamp", "generic", "Explain Java clamping", "T6",
            "public static int clamp(int value, int minimum, int maximum) {\n"
            "    return Math.max(minimum, Math.min(value, maximum));\n}",
            use_rag=False, description=description,
        ),
        _row(
            "generic_t6_adult", "generic", "Explain an age check", "T6",
            "public static boolean isAdult(int age) {\n"
            "    return age >= 18;\n}",
            use_rag=False, description=description,
        ),
        _row(
            "generic_t6_positive_sum", "generic", "Explain positive-value summing", "T6",
            "public static int sumPositive(int[] values) {\n"
            "    int total = 0;\n"
            "    for (int value : values) {\n"
            "        if (value > 0) total += value;\n"
            "    }\n"
            "    return total;\n}",
            use_rag=False, description=description,
        ),
    ]


def _ledgerflow_examples() -> List[Dict[str, Any]]:
    generation_description = (
        "The prompt omits repository-specific implementation details; RAG should "
        "recover them from the bundled LedgerFlow repository."
    )
    migration_description = (
        "A compact, valid migration input paired with an implementation in LedgerFlow."
    )
    explanation_description = "Valid LedgerFlow policy code for explanation."

    transfer_python = (
        "def transfer_risk_score(amount, tenure_days, country, trusted):\n"
        "    score = 40 if amount >= 250000 else 25 if amount >= 100000 else 0\n"
        "    score += 20 if tenure_days < 30 else 0\n"
        "    score += 30 if country.upper() in {'IR', 'KP', 'SY'} else 0\n"
        "    score += 15 if not trusted else 0\n"
        "    return min(score, 100)"
    )
    risk_python = (
        "def calculate_risk_score(amount: float, average: float, new_payee: bool) -> float:\n"
        "    score = 0.0\n"
        "    if average > 0 and amount > average * 3:\n"
        "        score += 50.0\n"
        "    if new_payee:\n"
        "        score += 25.0\n"
        "    return min(score, 100.0)"
    )
    pan_python = (
        "def validate_pan(pan_number: str) -> bool:\n"
        "    value = pan_number.strip().upper()\n"
        "    return len(value) == 10 and value[:5].isalpha() and "
        "value[5:9].isdigit() and value[-1].isalpha()"
    )
    transfer_java = (
        "public double dailyTransferLimit(String accountTier) {\n"
        "    return switch (accountTier.trim().toUpperCase()) {\n"
        "        case \"STANDARD\" -> 100000.0;\n"
        "        case \"PREMIUM\" -> 500000.0;\n"
        "        case \"PRIVATE\" -> 2000000.0;\n"
        "        default -> 50000.0;\n"
        "    };\n}"
    )
    fraud_java = (
        "public boolean flagSuspiciousTransaction(double riskScore, double threshold) {\n"
        "    return riskScore >= threshold;\n}"
    )
    pan_java = (
        "public String maskPan(String panNumber) {\n"
        "    String value = panNumber.trim().toUpperCase();\n"
        "    return value.substring(0, 3) + \"****\" + value.substring(7);\n}"
    )

    return [
        # T1
        _row(
            "ledgerflow_t1_transfer", "ledgerflow", "Implement transfer-risk policy", "T1",
            "Implement transfer_risk_score(amount, customer_tenure_days, "
            "destination_country, trusted_device) using this repository's exact "
            "thresholds, weights, country rules and score cap."
            + PYTHON_GENERATION_SUFFIX,
            use_rag=True, description=generation_description,
            expected_sources=["transfer_risk_score"],
        ),
        _row(
            "ledgerflow_t1_pan", "ledgerflow", "Implement PAN validation", "T1",
            "Implement validate_pan(pan_number) using LedgerFlow's exact normalization "
            "and PAN-format rules." + PYTHON_GENERATION_SUFFIX,
            use_rag=True, description=generation_description,
            expected_sources=["validate_pan"],
        ),
        _row(
            "ledgerflow_t1_loan", "ledgerflow", "Implement loan eligibility", "T1",
            "Implement calculate_eligible_amount(monthly_income, existing_emis, "
            "credit_score) using this repository's exact limits and edge cases."
            + PYTHON_GENERATION_SUFFIX,
            use_rag=True, description=generation_description,
            expected_sources=["calculate_eligible_amount"],
        ),

        # T2
        _row(
            "ledgerflow_t2_transfer", "ledgerflow", "Implement Java transfer risk", "T2",
            "Implement public class TransferPolicy with method transferRiskScore using "
            "LedgerFlow's exact transfer-risk thresholds, weights, countries and cap."
            + JAVA_GENERATION_SUFFIX,
            use_rag=True, description=generation_description,
            expected_sources=["transferRiskScore", "transfer_risk_score"],
        ),
        _row(
            "ledgerflow_t2_fraud", "ledgerflow", "Implement Java fraud score", "T2",
            "Implement public class FraudDetector with method calculateRiskScore using "
            "LedgerFlow's exact amount, average-transaction and new-payee rules."
            + JAVA_GENERATION_SUFFIX,
            use_rag=True, description=generation_description,
            expected_sources=["calculateRiskScore", "calculate_risk_score"],
        ),
        _row(
            "ledgerflow_t2_pan", "ledgerflow", "Implement Java PAN validation", "T2",
            "Implement public class KycValidator with method validatePan using the "
            "repository's exact PAN normalization and validation rules."
            + JAVA_GENERATION_SUFFIX,
            use_rag=True, description=generation_description,
            expected_sources=["validatePan", "validate_pan"],
        ),

        # T3
        _row(
            "ledgerflow_t3_step_up", "ledgerflow", "Migrate step-up authentication", "T3",
            "def requires_step_up_auth(risk_score: float) -> bool:\n"
            "    return risk_score >= 50.0",
            use_rag=True, description=migration_description,
            expected_sources=["requiresStepUpAuth"],
            source_path="policies/transfer_policy.py",
        ),
        _row(
            "ledgerflow_t3_fraud", "ledgerflow", "Migrate fraud-risk scoring", "T3",
            risk_python,
            use_rag=True, description=migration_description,
            expected_sources=["calculateRiskScore"],
            source_path="transactions/fraud_detector.py",
        ),
        _row(
            "ledgerflow_t3_pan", "ledgerflow", "Migrate PAN validation", "T3",
            pan_python,
            use_rag=True, description=migration_description,
            expected_sources=["validatePan"],
            source_path="accounts/kyc_validator.py",
        ),

        # T4
        _row(
            "ledgerflow_t4_limit", "ledgerflow", "Migrate daily transfer limit", "T4",
            transfer_java,
            use_rag=True, description=migration_description,
            expected_sources=["daily_transfer_limit"],
            source_path="policies/TransferPolicy.java",
        ),
        _row(
            "ledgerflow_t4_fraud", "ledgerflow", "Migrate fraud threshold", "T4",
            fraud_java,
            use_rag=True, description=migration_description,
            expected_sources=["flag_suspicious_transaction"],
            source_path="transactions/FraudDetector.java",
        ),
        _row(
            "ledgerflow_t4_pan", "ledgerflow", "Migrate PAN masking", "T4",
            pan_java,
            use_rag=True, description=migration_description,
            expected_sources=["mask_pan"],
            source_path="accounts/KycValidator.java",
        ),

        # T5
        _row(
            "ledgerflow_t5_transfer", "ledgerflow", "Explain transfer risk", "T5",
            transfer_python,
            use_rag=True, description=explanation_description,
            expected_sources=["transfer_risk_score"],
            source_path="policies/transfer_policy.py",
        ),
        _row(
            "ledgerflow_t5_fraud", "ledgerflow", "Explain fraud scoring", "T5",
            risk_python,
            use_rag=True, description=explanation_description,
            expected_sources=["calculate_risk_score"],
            source_path="transactions/fraud_detector.py",
        ),
        _row(
            "ledgerflow_t5_pan", "ledgerflow", "Explain PAN validation", "T5",
            pan_python,
            use_rag=True, description=explanation_description,
            expected_sources=["validate_pan"],
            source_path="accounts/kyc_validator.py",
        ),

        # T6
        _row(
            "ledgerflow_t6_limit", "ledgerflow", "Explain Java transfer limits", "T6",
            transfer_java,
            use_rag=True, description=explanation_description,
            expected_sources=["dailyTransferLimit"],
            source_path="policies/TransferPolicy.java",
        ),
        _row(
            "ledgerflow_t6_fraud", "ledgerflow", "Explain Java fraud threshold", "T6",
            fraud_java,
            use_rag=True, description=explanation_description,
            expected_sources=["flagSuspiciousTransaction"],
            source_path="transactions/FraudDetector.java",
        ),
        _row(
            "ledgerflow_t6_pan", "ledgerflow", "Explain Java PAN masking", "T6",
            pan_java,
            use_rag=True, description=explanation_description,
            expected_sources=["maskPan"],
            source_path="accounts/KycValidator.java",
        ),
    ]


def _python_functions(root: Path, limit: int = 3) -> List[tuple[str, Optional[str]]]:
    found: List[tuple[str, Optional[str]]] = []
    if root.is_dir():
        for path in sorted(root.rglob("*.py")):
            try:
                text = path.read_text(encoding="utf-8")
                tree = ast.parse(text)
            except Exception:
                continue
            for node in ast.walk(tree):
                if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    continue
                snippet = ast.get_source_segment(text, node)
                if snippet and 60 <= len(snippet) <= 1200:
                    found.append((snippet, path.relative_to(root).as_posix()))
                    if len(found) == limit:
                        return found
    return found


def _java_methods(root: Path, limit: int = 3) -> List[tuple[str, Optional[str]]]:
    found: List[tuple[str, Optional[str]]] = []
    pattern = re.compile(
        r"(?m)^\s*(?:public|private|protected)\s+(?:static\s+)?[^;{}]+\([^;{}]*\)\s*\{"
    )
    if root.is_dir():
        for path in sorted(root.rglob("*.java")):
            try:
                text = path.read_text(encoding="utf-8")
            except Exception:
                continue
            for match in pattern.finditer(text):
                start = match.start()
                opening = text.find("{", start)
                depth = 0
                state = "code"
                escaped = False
                index = opening
                while index < min(len(text), opening + 1600):
                    char = text[index]
                    nxt = text[index + 1] if index + 1 < len(text) else ""
                    if state == "line_comment":
                        if char == "\n":
                            state = "code"
                    elif state == "block_comment":
                        if char == "*" and nxt == "/":
                            state = "code"
                            index += 1
                    elif state in {"string", "char"}:
                        if escaped:
                            escaped = False
                        elif char == "\\":
                            escaped = True
                        elif (state == "string" and char == '"') or (
                            state == "char" and char == "'"
                        ):
                            state = "code"
                    else:
                        if char == "/" and nxt == "/":
                            state = "line_comment"
                            index += 1
                        elif char == "/" and nxt == "*":
                            state = "block_comment"
                            index += 1
                        elif char == '"':
                            state = "string"
                        elif char == "'":
                            state = "char"
                        elif char == "{":
                            depth += 1
                        elif char == "}":
                            depth -= 1
                            if depth == 0:
                                snippet = text[start:index + 1].strip()
                                if 60 <= len(snippet) <= 1500:
                                    found.append(
                                        (snippet, path.relative_to(root).as_posix())
                                    )
                                    if len(found) == limit:
                                        return found
                                break
                    index += 1
    return found


AWS_PYTHON_FALLBACKS = [
    (
        "def list_bucket_keys(s3_client, bucket_name):\n"
        "    response = s3_client.list_objects_v2(Bucket=bucket_name)\n"
        "    return [item['Key'] for item in response.get('Contents', [])]",
        None,
    ),
    (
        "def upload_text(s3_client, bucket_name, object_key, text):\n"
        "    return s3_client.put_object(Bucket=bucket_name, Key=object_key, Body=text.encode('utf-8'))",
        None,
    ),
    (
        "def bucket_exists(s3_client, bucket_name):\n"
        "    names = [item['Name'] for item in s3_client.list_buckets().get('Buckets', [])]\n"
        "    return bucket_name in names",
        None,
    ),
]

AWS_JAVA_FALLBACKS = [
    (
        "public static void listBuckets(S3Client s3) {\n"
        "    s3.listBuckets().buckets().forEach(bucket -> System.out.println(bucket.name()));\n}",
        None,
    ),
    (
        "public static boolean bucketExists(S3Client s3, String name) {\n"
        "    return s3.listBuckets().buckets().stream().anyMatch(bucket -> bucket.name().equals(name));\n}",
        None,
    ),
    (
        "public static void deleteObject(S3Client s3, String bucket, String key) {\n"
        "    s3.deleteObject(builder -> builder.bucket(bucket).key(key));\n}",
        None,
    ),
]


def _ensure_three(
    values: List[tuple[str, Optional[str]]],
    fallbacks: List[tuple[str, Optional[str]]],
) -> List[tuple[str, Optional[str]]]:
    result = list(values[:3])
    for fallback in fallbacks:
        if len(result) >= 3:
            break
        if fallback[0] not in {item[0] for item in result}:
            result.append(fallback)
    return result


def _aws_examples(project_root: str | Path | None) -> List[Dict[str, Any]]:
    root = repository_path("aws_s3", project_root=project_root)
    python_root = root / "python" / "example_code" / "s3" if root else Path()
    java_root = root / "javav2" / "example_code" / "s3" if root else Path()
    python_samples = _ensure_three(
        _python_functions(python_root), AWS_PYTHON_FALLBACKS
    )
    java_samples = _ensure_three(
        _java_methods(java_root), AWS_JAVA_FALLBACKS
    )
    description = (
        "An AWS S3 example loaded from the checked-out public repository when "
        "available, with a valid representative fallback otherwise."
    )
    rows: List[Dict[str, Any]] = []

    python_prompts = [
        (
            "Generate Python S3 upload helper",
            "Using this repository's boto3 conventions, implement upload_file(" 
            "s3_client, local_path, bucket_name, object_key).",
            ["upload_file"],
        ),
        (
            "Generate Python S3 listing helper",
            "Using this repository's boto3 conventions, implement list_bucket_keys(" 
            "s3_client, bucket_name) and handle a bucket with no Contents key.",
            ["list_objects", "list_bucket"],
        ),
        (
            "Generate Python S3 download helper",
            "Using this repository's boto3 conventions, implement download_file(" 
            "s3_client, bucket_name, object_key, local_path).",
            ["download_file", "get_object"],
        ),
    ]
    java_prompts = [
        (
            "Generate Java S3 download helper",
            "Using this repository's AWS SDK for Java v2 conventions, implement "
            "public class S3Downloader with a static download method.",
            ["getObject", "download"],
        ),
        (
            "Generate Java S3 bucket listing",
            "Using this repository's AWS SDK for Java v2 conventions, implement "
            "public class S3BucketLister with a static listBucketNames method.",
            ["listBuckets"],
        ),
        (
            "Generate Java S3 object deletion",
            "Using this repository's AWS SDK for Java v2 conventions, implement "
            "public class S3ObjectDeleter with a static delete method.",
            ["deleteObject"],
        ),
    ]

    for index, (title, prompt, expected) in enumerate(python_prompts, 1):
        rows.append(
            _row(
                f"aws_t1_{index}", "aws_s3", title, "T1",
                prompt + PYTHON_GENERATION_SUFFIX,
                use_rag=True, description=description,
                expected_sources=expected,
            )
        )
    for index, (title, prompt, expected) in enumerate(java_prompts, 1):
        rows.append(
            _row(
                f"aws_t2_{index}", "aws_s3", title, "T2",
                prompt + JAVA_GENERATION_SUFFIX,
                use_rag=True, description=description,
                expected_sources=expected,
            )
        )

    for index, (snippet, path) in enumerate(python_samples, 1):
        rows.append(
            _row(
                f"aws_t3_{index}", "aws_s3", f"Migrate Python S3 function {index}",
                "T3", snippet, use_rag=True, description=description,
                source_path=path,
            )
        )
        rows.append(
            _row(
                f"aws_t5_{index}", "aws_s3", f"Explain Python S3 function {index}",
                "T5", snippet, use_rag=True, description=description,
                source_path=path,
            )
        )
    for index, (snippet, path) in enumerate(java_samples, 1):
        rows.append(
            _row(
                f"aws_t4_{index}", "aws_s3", f"Migrate Java S3 method {index}",
                "T4", snippet, use_rag=True, description=description,
                source_path=path,
            )
        )
        rows.append(
            _row(
                f"aws_t6_{index}", "aws_s3", f"Explain Java S3 method {index}",
                "T6", snippet, use_rag=True, description=description,
                source_path=path,
            )
        )
    return rows


def _validate_catalogue(examples: List[Dict[str, Any]]) -> None:
    ids = [row["showcase_id"] for row in examples]
    if len(ids) != len(set(ids)):
        raise ValueError("Showcase identifiers must be unique.")
    if any(not str(row.get("input_text", "")).strip() for row in examples):
        raise ValueError("Every showcase must contain a non-empty input.")

    counts = Counter(
        (row["repository_id"], row["task_id"])
        for row in examples
    )
    missing = {
        f"{repository_id}/{task_id}": counts[(repository_id, task_id)]
        for repository_id in REPOSITORY_IDS
        for task_id in TASK_IO
        if counts[(repository_id, task_id)] < MINIMUM_EXAMPLES_PER_SECTION
    }
    if missing:
        raise ValueError(
            "Every repository/task section requires at least three examples: "
            f"{missing}"
        )

    # Inputs to Python-source tasks must themselves parse before being offered.
    invalid_python = []
    for row in examples:
        if row["task_id"] not in {"T3", "T5"}:
            continue
        try:
            ast.parse(row["input_text"])
        except SyntaxError as exc:
            invalid_python.append((row["showcase_id"], str(exc)))
    if invalid_python:
        raise ValueError(f"Invalid Python showcase inputs: {invalid_python}")


def showcase_examples(project_root: str | Path | None = None) -> List[Dict[str, Any]]:
    """Return three validated options for every repository/task section."""

    examples = (
        _generic_examples()
        + _ledgerflow_examples()
        + _aws_examples(project_root)
    )
    _validate_catalogue(examples)
    return examples
