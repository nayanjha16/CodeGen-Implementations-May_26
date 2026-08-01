"""Standalone Docker functional-correctness evaluator for RepoCoder Studio.

Runs entirely on the standard library -- no torch/transformers/faiss, no
`src.*` package imports, no network access except pulling the two Docker
images the first time. Designed to run on a machine that has real generation
results (produced separately, e.g. in the Colab notebook) but no GPU and no
project checkout: only this one file, plus Docker, is required.

What it does
------------
1. Self-test: runs the curated cases against known-correct source (the
   project's own demo-repo functions, embedded below) to prove the Docker
   harness itself works, before trusting it to judge model output.
2. Verification: if `no_rag_python.txt` / `rag_python.txt` / `no_rag_java.txt`
   / `rag_java.txt` exist in the current directory, runs the same functional
   comparison the notebook's Cell 26D runs, using whatever code you pasted
   into those files.
3. Prints one JSON object to stdout (copy it back into Colab and use
   RUNBOOK.md Step 8 to merge its Docker-dependent sections into
   "outputs/reports/functional_eval_report.json" without replacing the
   Colab-generated evidence) and also saves it to
   `functional_eval_report.json` next to this script.

Usage
-----
    python3 repocoder_docker_eval.py

See RUNBOOK.md for the full step-by-step (EC2 setup, Docker install, how to
get the four *.txt files onto this machine).
"""

from __future__ import annotations

import json
import re
import shutil
import subprocess
import tempfile
import uuid
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional

# ============================================================
# extract_code() -- verbatim copy of src/code_extraction.py
# ============================================================


def extract_code(prediction: str, language: str) -> str:
    text = prediction or ""
    fence = re.search(r"```(?:python|py|java)?\s*(.*?)```", text, flags=re.IGNORECASE | re.DOTALL)
    if fence:
        text = fence.group(1).strip()
    text = re.sub(r"^(Here is|Sure, here is|The code is|Below is).*?:", "", text, flags=re.I | re.S).strip()
    if language.lower() == "python":
        for marker in ["###", "```", "Explanation:", "Java:"]:
            if marker in text:
                text = text.split(marker, 1)[0].strip()
    if language.lower() == "java":
        for marker in ["###", "```", "Explanation:", "Python:"]:
            if marker in text:
                text = text.split(marker, 1)[0].strip()
    return text.strip()


# ============================================================
# Functional-eval harness -- verbatim copy of
# src/functional_execution_eval.py
# ============================================================


@dataclass(frozen=True)
class FunctionalCase:
    case_id: str
    function_name: str
    args: List[Any]
    kwargs: Dict[str, Any]
    expected: Any


@dataclass(frozen=True)
class JavaFunctionalCase:
    case_id: str
    class_name: str
    method_name: str
    arg_literals: List[str] = field(default_factory=list)
    expected_literal: str = "null"
    static: bool = False


@dataclass(frozen=True)
class FunctionalResult:
    case_id: str
    status: str
    passed: bool
    detail: str = ""


_RUNNER = r"""
import importlib.util
import json
import sys

spec = importlib.util.spec_from_file_location("candidate", "/work/candidate.py")
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
cases = json.load(open("/work/cases.json", encoding="utf-8"))
results = []
for case in cases:
    try:
        fn = getattr(module, case["function_name"])
        actual = fn(*case.get("args", []), **case.get("kwargs", {}))
        passed = actual == case.get("expected")
        results.append({
            "case_id": case["case_id"],
            "status": "PASS" if passed else "FAIL",
            "passed": passed,
            "detail": "" if passed else f"expected={case.get('expected')!r}, actual={actual!r}",
        })
    except Exception as exc:
        results.append({
            "case_id": case["case_id"],
            "status": "ERROR",
            "passed": False,
            "detail": f"{type(exc).__name__}: {exc}",
        })
print(json.dumps(results))
"""


def _docker_available() -> bool:
    if shutil.which("docker") is None:
        return False
    try:
        completed = subprocess.run(
            ["docker", "info", "--format", "{{.ServerVersion}}"],
            check=False, capture_output=True, text=True, timeout=5,
        )
        return completed.returncode == 0
    except (OSError, subprocess.SubprocessError):
        return False


def _ensure_docker_image(image: str, timeout_seconds: int) -> Optional[str]:
    try:
        inspect = subprocess.run(
            ["docker", "image", "inspect", image],
            check=False, capture_output=True, text=True, timeout=10,
        )
        if inspect.returncode == 0:
            return None
        pull = subprocess.run(
            ["docker", "pull", image],
            check=False, capture_output=True, text=True, timeout=timeout_seconds,
        )
        if pull.returncode == 0:
            return None
        return (pull.stderr or pull.stdout or "Docker image pull failed")[-2000:]
    except subprocess.TimeoutExpired:
        return f"Docker image pull/inspect timed out after {timeout_seconds} seconds"
    except OSError as exc:
        return f"Docker image could not be prepared: {exc}"


def _isolation_flags(container_name: str, memory: str, cpus: str, tmpfs_size: str) -> List[str]:
    return [
        "--name", container_name,
        "--network", "none",
        "--read-only",
        "--user", "65534:65534",
        "--memory", memory,
        "--cpus", cpus,
        "--pids-limit", "64",
        "--cap-drop", "ALL",
        "--security-opt", "no-new-privileges",
        "--tmpfs", f"/tmp:rw,noexec,nosuid,size={tmpfs_size}",
    ]


def _kill_container(name: str) -> None:
    try:
        subprocess.run(["docker", "kill", name], check=False, capture_output=True, timeout=5)
    except (OSError, subprocess.SubprocessError):
        pass


def _run_docker(command: List[str], timeout_seconds: int, container_name: str):
    try:
        completed = subprocess.run(
            command, check=False, capture_output=True, text=True, timeout=timeout_seconds,
        )
        return completed, None
    except subprocess.TimeoutExpired:
        _kill_container(container_name)
        return None, _summary([], "TIMEOUT", "container execution timed out")
    except OSError as exc:
        return None, _summary([], "NOT_FEASIBLE", f"Docker could not start: {exc}")


def _summary(results: List[FunctionalResult], status: str, reason: str) -> Dict[str, Any]:
    passed = sum(result.passed for result in results)
    return {
        "status": status,
        "reason": reason,
        "cases": [asdict(result) for result in results],
        "cases_run": len(results),
        "cases_passed": passed,
        "pass_rate": passed / len(results) if results else None,
        "execution_isolated": status != "NOT_FEASIBLE",
        "isolation": "docker:no-network,read-only,resource-limited",
    }


class DockerPythonEvaluator:
    def __init__(self, image="python:3.11-slim", timeout_seconds=15, memory="256m", cpus="0.5", image_pull_timeout_seconds=300):
        self.image = image
        self.timeout_seconds = timeout_seconds
        self.image_pull_timeout_seconds = image_pull_timeout_seconds
        self.memory = memory
        self.cpus = cpus

    @staticmethod
    def available() -> bool:
        return _docker_available()

    def evaluate(self, code: str, cases: Iterable[FunctionalCase]) -> Dict[str, Any]:
        cases = list(cases)
        if not cases:
            return _summary([], "NOT_FEASIBLE", "no trusted functional cases")
        if not self.available():
            return _summary([], "NOT_FEASIBLE", "Docker is unavailable; code was not executed")
        image_error = _ensure_docker_image(self.image, self.image_pull_timeout_seconds)
        if image_error is not None:
            return _summary([], "NOT_FEASIBLE", image_error)

        with tempfile.TemporaryDirectory(prefix="repocoder_functional_") as temp:
            root = Path(temp)
            candidate_path = root / "candidate.py"
            runner_path = root / "runner.py"
            cases_path = root / "cases.json"
            candidate_path.write_text(code or "", encoding="utf-8")
            runner_path.write_text(_RUNNER, encoding="utf-8")
            cases_path.write_text(json.dumps([asdict(c) for c in cases]), encoding="utf-8")
            # TemporaryDirectory is 0700 on Linux. The evaluator container
            # deliberately runs as UID/GID 65534, so make only this ephemeral
            # read-only bind-mount tree traversable/readable by that user.
            root.chmod(0o755)
            for path in (candidate_path, runner_path, cases_path):
                path.chmod(0o644)
            container_name = f"repocoder-func-eval-{uuid.uuid4().hex[:12]}"
            command = [
                "docker", "run", "--rm",
                *_isolation_flags(container_name, self.memory, self.cpus, "16m"),
                "-v", f"{root.resolve()}:/work:ro",
                self.image, "python", "-I", "/work/runner.py",
            ]
            completed, error = _run_docker(command, self.timeout_seconds, container_name)
            if error is not None:
                return error
            if completed.returncode != 0:
                detail = (completed.stderr or completed.stdout or "container failed")[-2000:]
                return _summary([], "ERROR", detail)
            try:
                rows = json.loads(completed.stdout.strip().splitlines()[-1])
                results = [FunctionalResult(**row) for row in rows]
            except (json.JSONDecodeError, IndexError, TypeError, ValueError) as exc:
                return _summary([], "ERROR", f"invalid runner output: {exc}")
            return _summary(results, "COMPLETE", "")


_JAVA_IDENTIFIER = re.compile(r"^[A-Za-z_$][A-Za-z0-9_$]*$")
_JAVA_PACKAGE = re.compile(r"(?m)^\s*package\s+([A-Za-z_$][A-Za-z0-9_$]*(?:\.[A-Za-z_$][A-Za-z0-9_$]*)*)\s*;")


def _java_package_name(code: str) -> str:
    match = _JAVA_PACKAGE.search(code or "")
    return match.group(1) if match else ""


def _java_runner_source(cases: List[JavaFunctionalCase], package_name: str = "") -> str:
    blocks = []
    for index, case in enumerate(cases):
        if not _JAVA_IDENTIFIER.fullmatch(case.class_name):
            raise ValueError(f"invalid Java class name in functional case: {case.class_name!r}")
        if not _JAVA_IDENTIFIER.fullmatch(case.method_name):
            raise ValueError(f"invalid Java method name in functional case: {case.method_name!r}")
        args_src = ", ".join(case.arg_literals)
        call = (
            f"{case.class_name}.{case.method_name}({args_src})"
            if case.static
            else f"new {case.class_name}().{case.method_name}({args_src})"
        )
        case_id = case.case_id.replace("\\", "\\\\").replace('"', '\\"')
        blocks.append(
            f"""
        try {{
            Object result{index} = {call};
            Object expected{index} = {case.expected_literal};
            boolean passed{index} = java.util.Objects.equals(result{index}, expected{index});
            out.append("{case_id}|" + (passed{index} ? "PASS" : "FAIL") + "|" +
                (passed{index} ? "" : ("expected=" + expected{index} + " actual=" + result{index})) + "\\n");
        }} catch (Throwable t{index}) {{
            out.append("{case_id}|ERROR|" + t{index}.getClass().getSimpleName() + ": " + t{index}.getMessage() + "\\n");
        }}"""
        )
    body = "\n".join(blocks)
    package_line = f"package {package_name};\n\n" if package_name else ""
    return f"""{package_line}public class Runner {{
    public static void main(String[] args) {{
        StringBuilder out = new StringBuilder();
{body}
        System.out.print(out);
    }}
}}
"""


class DockerJavaEvaluator:
    def __init__(self, image="eclipse-temurin:17-jdk-alpine", timeout_seconds=20, memory="384m", cpus="0.5", image_pull_timeout_seconds=300):
        self.image = image
        self.timeout_seconds = timeout_seconds
        self.image_pull_timeout_seconds = image_pull_timeout_seconds
        self.memory = memory
        self.cpus = cpus

    @staticmethod
    def available() -> bool:
        return _docker_available()

    def evaluate(self, code: str, class_name: str, cases: Iterable[JavaFunctionalCase]) -> Dict[str, Any]:
        cases = list(cases)
        if not cases:
            return _summary([], "NOT_FEASIBLE", "no trusted functional cases")
        if not self.available():
            return _summary([], "NOT_FEASIBLE", "Docker is unavailable; code was not executed")
        image_error = _ensure_docker_image(self.image, self.image_pull_timeout_seconds)
        if image_error is not None:
            return _summary([], "NOT_FEASIBLE", image_error)
        if not _JAVA_IDENTIFIER.fullmatch(class_name or ""):
            return _summary([], "ERROR", f"invalid Java class name: {class_name!r}")

        package_name = _java_package_name(code)
        runner_class = f"{package_name}.Runner" if package_name else "Runner"

        with tempfile.TemporaryDirectory(prefix="repocoder_functional_java_") as temp:
            root = Path(temp)
            candidate_path = root / f"{class_name}.java"
            candidate_path.write_text(code or "", encoding="utf-8")
            try:
                runner_source = _java_runner_source(cases, package_name=package_name)
            except ValueError as exc:
                return _summary([], "ERROR", str(exc))
            runner_path = root / "Runner.java"
            runner_path.write_text(runner_source, encoding="utf-8")
            # See DockerPythonEvaluator: the non-root container must be able
            # to traverse the host temporary directory and read both sources.
            root.chmod(0o755)
            for path in (candidate_path, runner_path):
                path.chmod(0o644)
            container_name = f"repocoder-func-eval-java-{uuid.uuid4().hex[:12]}"
            command = [
                "docker", "run", "--rm",
                *_isolation_flags(container_name, self.memory, self.cpus, "48m"),
                "-e", "HOME=/tmp",
                "-v", f"{root.resolve()}:/work:ro",
                self.image, "sh", "-c",
                f"javac -d /tmp /work/*.java && java -cp /tmp {runner_class}",
            ]
            completed, error = _run_docker(command, self.timeout_seconds, container_name)
            if error is not None:
                return error
            if completed.returncode != 0:
                detail = (completed.stderr or completed.stdout or "container failed")[-2000:]
                return _summary([], "ERROR", detail)
            try:
                results = []
                for line in completed.stdout.splitlines():
                    if not line.strip():
                        continue
                    case_id, status, detail = line.split("|", 2)
                    results.append(FunctionalResult(case_id=case_id, status=status, passed=(status == "PASS"), detail=detail))
                if len(results) != len(cases):
                    return _summary(results, "ERROR", f"expected {len(cases)} result lines, got {len(results)}")
            except ValueError as exc:
                return _summary([], "ERROR", f"invalid runner output: {exc}")
            return _summary(results, "COMPLETE", "")


def compare_functional_outputs(no_rag_code, rag_code, cases, evaluator=None) -> Dict[str, Any]:
    evaluator = evaluator or DockerPythonEvaluator()
    cases = list(cases)
    no_rag = evaluator.evaluate(extract_code(no_rag_code, "python"), cases)
    with_rag = evaluator.evaluate(extract_code(rag_code, "python"), cases)
    return {"no_rag": no_rag, "with_rag": with_rag, "pass_rate_lift": _pass_rate_lift(no_rag, with_rag)}


def compare_java_functional_outputs(no_rag_code, rag_code, class_name, cases, evaluator=None) -> Dict[str, Any]:
    evaluator = evaluator or DockerJavaEvaluator()
    cases = list(cases)
    no_rag = evaluator.evaluate(extract_code(no_rag_code, "java"), class_name, cases)
    with_rag = evaluator.evaluate(extract_code(rag_code, "java"), class_name, cases)
    return {"no_rag": no_rag, "with_rag": with_rag, "pass_rate_lift": _pass_rate_lift(no_rag, with_rag)}


def _pass_rate_lift(no_rag, with_rag) -> Optional[float]:
    no_rate = no_rag.get("pass_rate")
    rag_rate = with_rag.get("pass_rate")
    if isinstance(no_rate, (int, float)) and isinstance(rag_rate, (int, float)):
        return rag_rate - no_rate
    return None


# ============================================================
# Self-test fixtures -- same cases and known-correct source as
# notebook Cell 26D, so results here are directly comparable to
# whatever Colab could not execute.
# ============================================================

PYTHON_CASES = [
    FunctionalCase("flag_below_threshold", "flag_suspicious_transaction", [69.9], {"threshold": 70.0}, False),
    FunctionalCase("flag_at_threshold", "flag_suspicious_transaction", [70.0], {"threshold": 70.0}, True),
    FunctionalCase("risk_score_moderate", "calculate_risk_score", [50000, 10000, False], {}, 50.0),
    FunctionalCase("risk_score_capped", "calculate_risk_score", [150000, 10000, True], {}, 100.0),
    FunctionalCase("round_amounts_flagged", "detect_round_amount_pattern", [[1000.0, 2000.0, 3000.0, 1500.0]], {}, True),
    FunctionalCase("round_amounts_clear", "detect_round_amount_pattern", [[1500.0, 2500.0]], {}, False),
    FunctionalCase("pan_valid", "validate_pan", ["ABCDE1234F"], {}, True),
    FunctionalCase("pan_invalid", "validate_pan", ["invalid"], {}, False),
    FunctionalCase("aadhaar_valid", "validate_aadhaar", ["123456789012"], {}, True),
    FunctionalCase("mask_pan_example", "mask_pan", ["abcde1234f"], {}, "******234F"),
    FunctionalCase("transfer_low_risk", "transfer_risk_score", [50000, 365, "US", True], {}, 0.0),
    FunctionalCase("transfer_amount_boundary", "transfer_risk_score", [100000, 365, "US", True], {}, 25.0),
    FunctionalCase("transfer_combined_risk", "transfer_risk_score", [120000, 10, "IR", False], {}, 90.0),
    FunctionalCase("transfer_risk_capped", "transfer_risk_score", [300000, 10, "SY", False], {}, 100.0),
]

FRAUD_DETECTOR_JAVA_CASES = [
    JavaFunctionalCase("flag_below_threshold", "FraudDetector", "flagSuspiciousTransaction", ["69.9", "70.0"], "false"),
    JavaFunctionalCase("flag_at_threshold", "FraudDetector", "flagSuspiciousTransaction", ["70.0", "70.0"], "true"),
    JavaFunctionalCase("risk_score_capped", "FraudDetector", "calculateRiskScore", ["150000", "10000", "true"], "100.0"),
]
KYC_VALIDATOR_JAVA_CASES = [
    JavaFunctionalCase("pan_valid", "KycValidator", "validatePan", ['"ABCDE1234F"'], "true"),
    JavaFunctionalCase("mask_pan_example", "KycValidator", "maskPan", ['"abcde1234f"'], '"******234F"'),
]
TRANSFER_POLICY_JAVA_CASES = [
    JavaFunctionalCase("transfer_low_risk", "TransferPolicy", "transferRiskScore", ["50000", "365", '"US"', "true"], "0.0"),
    JavaFunctionalCase("transfer_amount_boundary", "TransferPolicy", "transferRiskScore", ["100000", "365", '"US"', "true"], "25.0"),
    JavaFunctionalCase("transfer_combined_risk", "TransferPolicy", "transferRiskScore", ["120000", "10", '"IR"', "false"], "90.0"),
    JavaFunctionalCase("transfer_risk_capped", "TransferPolicy", "transferRiskScore", ["300000", "10", '"SY"', "false"], "100.0"),
]

PYTHON_SELF_TEST_SOURCE = '''
import re


def flag_suspicious_transaction(risk_score, threshold=70.0):
    return risk_score >= threshold


def calculate_risk_score(amount, account_avg_transaction, is_new_payee):
    score = 0.0
    if account_avg_transaction > 0:
        ratio = amount / account_avg_transaction
        score += min(ratio * 10, 60)
    if is_new_payee:
        score += 25
    if amount > 100_000:
        score += 15
    return min(score, 100.0)


def detect_round_amount_pattern(amounts):
    round_count = sum(1 for a in amounts if a % 1000 == 0 and a > 0)
    return len(amounts) > 0 and (round_count / len(amounts)) > 0.6


def validate_pan(pan_number):
    return bool(re.fullmatch(r"[A-Z]{5}[0-9]{4}[A-Z]{1}", pan_number.strip().upper()))


def validate_aadhaar(aadhaar_number):
    digits = aadhaar_number.replace(" ", "")
    return digits.isdigit() and len(digits) == 12


def mask_pan(pan_number):
    pan_number = pan_number.strip().upper()
    if len(pan_number) < 4:
        return "*" * len(pan_number)
    return "*" * (len(pan_number) - 4) + pan_number[-4:]


def transfer_risk_score(amount, customer_tenure_days, destination_country, trusted_device):
    high_risk_countries = {"IR", "KP", "SY"}
    score = 0.0
    if amount >= 250_000:
        score += 40
    elif amount >= 100_000:
        score += 25
    if customer_tenure_days < 30:
        score += 20
    if destination_country.strip().upper() in high_risk_countries:
        score += 30
    if not trusted_device:
        score += 15
    return min(score, 100.0)
'''

# Verbatim copies of repo_explorer_data/sample_repo/transactions/FraudDetector.java
# and .../accounts/KycValidator.java -- the two already-migrated demo classes.
FRAUD_DETECTOR_JAVA_SOURCE = '''package transactions;

import java.util.List;
import java.time.LocalDateTime;
import java.time.temporal.ChronoUnit;

/**
 * Fraud detection heuristics for the demo BFSI sample repository.
 *
 * Java counterpart of transactions/fraud_detector.py -- same heuristics,
 * kept in step with the Python version so Stage 4/5 has a genuinely
 * bilingual repository to index rather than a Python-only demo.
 */
public class FraudDetector {

    /**
     * Compute a 0-100 fraud risk score for a transaction based on amount
     * and payee history.
     */
    public double calculateRiskScore(double amount, double accountAvgTransaction, boolean isNewPayee) {
        double score = 0.0;
        if (accountAvgTransaction > 0) {
            double ratio = amount / accountAvgTransaction;
            score += Math.min(ratio * 10, 60);
        }
        if (isNewPayee) {
            score += 25;
        }
        if (amount > 100000) {
            score += 15;
        }
        return Math.min(score, 100.0);
    }

    /**
     * Decide whether a transaction should be flagged for manual fraud
     * review.
     */
    public boolean flagSuspiciousTransaction(double riskScore, double threshold) {
        return riskScore >= threshold;
    }

    /**
     * Return true if too many transactions have occurred within a short
     * time window (velocity fraud check).
     */
    public boolean checkVelocityLimit(List<LocalDateTime> recentTransactionTimes, int windowMinutes, int maxCount) {
        if (recentTransactionTimes.isEmpty()) {
            return false;
        }
        LocalDateTime cutoff = LocalDateTime.now().minus(windowMinutes, ChronoUnit.MINUTES);
        int recentCount = 0;
        for (LocalDateTime t : recentTransactionTimes) {
            if (!t.isBefore(cutoff)) {
                recentCount++;
            }
        }
        return recentCount > maxCount;
    }

    /**
     * Flag a suspicious pattern of suspiciously round transaction
     * amounts, often seen in structuring/smurfing.
     */
    public boolean detectRoundAmountPattern(List<Double> amounts) {
        if (amounts.isEmpty()) {
            return false;
        }
        long roundCount = 0;
        for (double a : amounts) {
            if (a > 0 && a % 1000 == 0) {
                roundCount++;
            }
        }
        return ((double) roundCount / amounts.size()) > 0.6;
    }
}
'''

KYC_VALIDATOR_JAVA_SOURCE = '''package accounts;

import java.util.HashMap;
import java.util.Map;

/**
 * Customer identity verification (KYC) for the demo BFSI sample repository.
 *
 * Java counterpart of accounts/kyc_validator.py -- same checks, kept in
 * step with the Python version so Stage 4/5 has a genuinely bilingual
 * repository to index rather than a Python-only demo.
 */
public class KycValidator {

    /**
     * Check whether a string matches the Indian PAN card format (5
     * letters, 4 digits, 1 letter).
     */
    public boolean validatePan(String panNumber) {
        String normalized = panNumber.trim().toUpperCase();
        return normalized.matches("[A-Z]{5}[0-9]{4}[A-Z]{1}");
    }

    /**
     * Check whether a string is a plausible 12-digit Aadhaar number.
     */
    public boolean validateAadhaar(String aadhaarNumber) {
        String digits = aadhaarNumber.replace(" ", "");
        return digits.matches("[0-9]+") && digits.length() == 12;
    }

    /**
     * Run full KYC identity verification, combining PAN and Aadhaar
     * checks.
     */
    public Map<String, Boolean> verifyIdentity(String panNumber, String aadhaarNumber, String fullName) {
        boolean panOk = validatePan(panNumber);
        boolean aadhaarOk = validateAadhaar(aadhaarNumber);
        boolean nameOk = fullName != null && !fullName.trim().isEmpty();

        Map<String, Boolean> result = new HashMap<>();
        result.put("verified", panOk && aadhaarOk && nameOk);
        result.put("panValid", panOk);
        result.put("aadhaarValid", aadhaarOk);
        result.put("nameProvided", nameOk);
        return result;
    }

    /**
     * Mask a PAN number for display, keeping only the last 4 characters
     * visible.
     */
    public String maskPan(String panNumber) {
        String normalized = panNumber.trim().toUpperCase();
        if (normalized.length() < 4) {
            return "*".repeat(normalized.length());
        }
        String visible = normalized.substring(normalized.length() - 4);
        return "*".repeat(normalized.length() - 4) + visible;
    }
}
'''

TRANSFER_POLICY_JAVA_SOURCE = '''package policies;

import java.util.Map;
import java.util.Set;

public class TransferPolicy {
    public double transferRiskScore(
        double amount, int customerTenureDays, String destinationCountry, boolean trustedDevice
    ) {
        Set<String> highRiskCountries = Set.of("IR", "KP", "SY");
        double score = 0.0;
        if (amount >= 250000) {
            score += 40;
        } else if (amount >= 100000) {
            score += 25;
        }
        if (customerTenureDays < 30) {
            score += 20;
        }
        if (highRiskCountries.contains(destinationCountry.trim().toUpperCase())) {
            score += 30;
        }
        if (!trustedDevice) {
            score += 15;
        }
        return Math.min(score, 100.0);
    }

    public boolean requiresStepUpAuth(double riskScore) {
        return riskScore >= 50.0;
    }

}
'''


def _not_feasible_pair(reason: str) -> Dict[str, Any]:
    result = {
        "status": "NOT_FEASIBLE", "reason": reason, "cases": [], "cases_run": 0,
        "cases_passed": 0, "pass_rate": None, "execution_isolated": False,
        "isolation": "docker:no-network,read-only,resource-limited",
    }
    return {"no_rag": dict(result), "with_rag": dict(result), "pass_rate_lift": None}


def _read_if_present(path: Path) -> Optional[str]:
    return path.read_text(encoding="utf-8") if path.exists() else None


def main() -> None:
    here = Path(__file__).resolve().parent
    docker_available = DockerPythonEvaluator.available()
    print(f"Docker daemon available: {docker_available}")

    python_evaluator = DockerPythonEvaluator()
    java_evaluator = DockerJavaEvaluator()

    print("\n--- Self-test (known-correct source) ---")
    python_self_test = python_evaluator.evaluate(PYTHON_SELF_TEST_SOURCE, PYTHON_CASES)
    print(f"Python: {python_self_test['status']} ({python_self_test['cases_passed']}/{python_self_test['cases_run']} passed)")

    java_self_test_results = {}
    if docker_available:
        java_self_test_results["FraudDetector"] = java_evaluator.evaluate(
            FRAUD_DETECTOR_JAVA_SOURCE, "FraudDetector", FRAUD_DETECTOR_JAVA_CASES
        )
        java_self_test_results["KycValidator"] = java_evaluator.evaluate(
            KYC_VALIDATOR_JAVA_SOURCE, "KycValidator", KYC_VALIDATOR_JAVA_CASES
        )
        java_self_test_results["TransferPolicy"] = java_evaluator.evaluate(
            TRANSFER_POLICY_JAVA_SOURCE, "TransferPolicy", TRANSFER_POLICY_JAVA_CASES
        )
    else:
        for class_name in ("FraudDetector", "KycValidator", "TransferPolicy"):
            java_self_test_results[class_name] = _not_feasible_pair(
                "Docker is unavailable; code was not executed"
            )["no_rag"]
    for class_name, result in java_self_test_results.items():
        print(f"Java ({class_name}): {result['status']} ({result['cases_passed']}/{result['cases_run']} passed)")

    print("\n--- Verification (generated code from Colab, if present) ---")
    no_rag_python = _read_if_present(here / "no_rag_python.txt")
    rag_python = _read_if_present(here / "rag_python.txt")
    no_rag_java = _read_if_present(here / "no_rag_java.txt")
    rag_java = _read_if_present(here / "rag_java.txt")

    python_harness_ready = python_self_test["status"] == "COMPLETE" and python_self_test["cases_passed"] == len(PYTHON_CASES)
    java_harness_ready = all(
        r["status"] == "COMPLETE" and r["cases_passed"] == r["cases_run"] and r["cases_run"] > 0
        for r in java_self_test_results.values()
    )

    if no_rag_python is not None and rag_python is not None:
        if python_harness_ready:
            python_verification = compare_functional_outputs(
                no_rag_python, rag_python, PYTHON_CASES[10:14], evaluator=python_evaluator
            )
        else:
            python_verification = _not_feasible_pair("Python Docker harness self-test did not pass.")
    else:
        python_verification = _not_feasible_pair(
            "no_rag_python.txt / rag_python.txt not found next to this script -- see RUNBOOK.md Step 6e."
        )

    if no_rag_java is not None and rag_java is not None:
        if java_harness_ready:
            java_verification = compare_java_functional_outputs(
                no_rag_java,
                rag_java,
                "TransferPolicy",
                TRANSFER_POLICY_JAVA_CASES,
                evaluator=java_evaluator,
            )
        else:
            java_verification = _not_feasible_pair("Java Docker harness self-test did not pass.")
    else:
        java_verification = _not_feasible_pair(
            "no_rag_java.txt / rag_java.txt not found next to this script -- see RUNBOOK.md Step 6e."
        )

    for language, comparison in (("python", python_verification), ("java", java_verification)):
        print(f"\n{language.title()} verification:")
        for mode in ("no_rag", "with_rag"):
            r = comparison[mode]
            print(f"  {mode}: {r['status']} ({r['cases_passed']}/{r['cases_run']} passed)")
            if r["status"] == "NOT_FEASIBLE":
                print(f"    Reason: {r['reason']}")
        print(f"  pass_rate_lift: {comparison['pass_rate_lift']}")

    report = {
        "python_self_test": python_self_test,
        "java_self_test": java_self_test_results,
        "verification": {"python": python_verification, "java": java_verification},
    }
    out_path = here / "functional_eval_report.json"
    out_path.write_text(json.dumps(report, indent=2), encoding="utf-8")

    print("\n" + "=" * 60)
    print("JSON result (copy everything below back into Colab):")
    print("=" * 60)
    print(json.dumps(report))
    print(f"\nAlso saved locally to {out_path}")


if __name__ == "__main__":
    main()
