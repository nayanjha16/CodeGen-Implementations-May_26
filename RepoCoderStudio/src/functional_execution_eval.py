"""Opt-in functional evaluation of generated Python or Java in a locked-down
Docker job.

Generated code is untrusted. Both evaluators refuse to execute unless a
Docker-compatible runtime is available. Neither ever silently falls back to
running model output in the notebook/kernel process.
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

from src.code_extraction import extract_code


@dataclass(frozen=True)
class FunctionalCase:
    case_id: str
    function_name: str
    args: List[Any]
    kwargs: Dict[str, Any]
    expected: Any


@dataclass(frozen=True)
class JavaFunctionalCase:
    """A Java functional test case, expressed as source-level literals
    rather than Python values (args: Python objects; args_literals: Java
    expressions like "70.0" or "\\"KYC123\\""). Java is statically typed, so
    the caller already has to know each parameter's type to write a correct
    case -- accepting literals directly avoids needing a JSON-to-Java-args
    bridge (with all its boxing/type-matching edge cases) inside the
    sandboxed runner. class_name must match the candidate code's public
    class name exactly (Java requires the file name to match it too)."""

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
            check=False,
            capture_output=True,
            text=True,
            timeout=5,
        )
        return completed.returncode == 0
    except (OSError, subprocess.SubprocessError):
        return False


def _ensure_docker_image(image: str, timeout_seconds: int) -> Optional[str]:
    """Ensure an evaluator image is local before the short execution timeout
    starts. An implicit pull inside ``docker run`` can easily exceed the
    candidate-execution timeout on a fresh machine and be misreported as a
    code timeout."""
    try:
        inspect = subprocess.run(
            ["docker", "image", "inspect", image],
            check=False,
            capture_output=True,
            text=True,
            timeout=10,
        )
        if inspect.returncode == 0:
            return None
        pull = subprocess.run(
            ["docker", "pull", image],
            check=False,
            capture_output=True,
            text=True,
            timeout=timeout_seconds,
        )
        if pull.returncode == 0:
            return None
        return (pull.stderr or pull.stdout or "Docker image pull failed")[-2000:]
    except subprocess.TimeoutExpired:
        return f"Docker image pull timed out after {timeout_seconds} seconds"
    except OSError as exc:
        return f"Docker image could not be prepared: {exc}"


def _isolation_flags(container_name: str, memory: str, cpus: str, tmpfs_size: str) -> List[str]:
    """Shared no-network / read-only / resource-limited / dropped-capability
    profile for both the Python and Java evaluators below."""
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
    """Best-effort cleanup for the timeout path: `--rm` only removes a
    container once it exits, and killing the local `docker run` client
    process does not, by itself, stop the container the daemon is still
    running. Failure here is swallowed -- it must never mask the TIMEOUT
    result this is called from."""
    try:
        subprocess.run(
            ["docker", "kill", name],
            check=False,
            capture_output=True,
            timeout=5,
        )
    except (OSError, subprocess.SubprocessError):
        pass


def _run_docker(
    command: List[str], timeout_seconds: int, container_name: str
) -> "tuple[Optional[subprocess.CompletedProcess], Optional[Dict[str, Any]]]":
    """Runs `command`, returning (completed_process, None) on a normal exit
    (including a non-zero return code -- the caller decides what that means),
    or (None, error_summary) if the run itself couldn't be interpreted at all
    (timeout, Docker missing)."""
    try:
        completed = subprocess.run(
            command,
            check=False,
            capture_output=True,
            text=True,
            timeout=timeout_seconds,
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
    """Execute Python test cases with no network, read-only root, an
    unprivileged user, resource limits, and a timeout."""

    def __init__(
        self,
        image: str = "python:3.11-slim",
        timeout_seconds: int = 15,
        memory: str = "256m",
        cpus: str = "0.5",
        image_pull_timeout_seconds: int = 300,
    ):
        self.image = image
        self.timeout_seconds = timeout_seconds
        self.image_pull_timeout_seconds = image_pull_timeout_seconds
        self.memory = memory
        self.cpus = cpus

    @staticmethod
    def available() -> bool:
        return _docker_available()

    def evaluate(
        self,
        code: str,
        cases: Iterable[FunctionalCase],
    ) -> Dict[str, Any]:
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
            cases_path.write_text(
                json.dumps([asdict(case) for case in cases]), encoding="utf-8"
            )
            # TemporaryDirectory is 0700 on Linux. The evaluator container
            # intentionally runs as UID/GID 65534, so it needs directory
            # traversal and read permission on the bind-mounted fixtures.
            root.chmod(0o755)
            for path in (candidate_path, runner_path, cases_path):
                path.chmod(0o644)
            # A deterministic name lets the timeout handler kill this specific
            # container -- subprocess.run(timeout=...) only kills the local
            # `docker run` client process, not the container the daemon is
            # still running, so without this a hung/looping candidate would
            # leave an orphaned container behind.
            container_name = f"repocoder-func-eval-{uuid.uuid4().hex[:12]}"
            command = [
                "docker", "run", "--rm",
                *_isolation_flags(container_name, self.memory, self.cpus, "16m"),
                "-v", f"{root.resolve()}:/work:ro",
                self.image,
                "python", "-I", "/work/runner.py",
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
_JAVA_PACKAGE = re.compile(
    r"(?m)^\s*package\s+([A-Za-z_$][A-Za-z0-9_$]*(?:\.[A-Za-z_$][A-Za-z0-9_$]*)*)\s*;"
)


def _java_package_name(code: str) -> str:
    match = _JAVA_PACKAGE.search(code or "")
    return match.group(1) if match else ""


def _java_runner_source(
    cases: List[JavaFunctionalCase],
    package_name: str = "",
) -> str:
    """Generates a small Java test driver that literally calls each case's
    method with its caller-supplied argument literals, rather than parsing
    JSON/reflecting on runtime types inside the sandbox -- see
    JavaFunctionalCase's docstring for why."""
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
    """Execute Java test cases with the same isolation profile as
    DockerPythonEvaluator, plus a compile step (the container needs a JDK,
    not just a JRE, since candidate.java is compiled at evaluation time).
    Comparing generated Java functionally (not just "does it compile", which
    java_validator.py already checks) closes the gap the Python-only
    functional evaluator left for T2/T3 (NL/Python -> Java)."""

    def __init__(
        self,
        image: str = "eclipse-temurin:17-jdk-alpine",
        timeout_seconds: int = 20,
        memory: str = "384m",
        cpus: str = "0.5",
        image_pull_timeout_seconds: int = 300,
    ):
        self.image = image
        self.timeout_seconds = timeout_seconds
        self.image_pull_timeout_seconds = image_pull_timeout_seconds
        self.memory = memory
        self.cpus = cpus

    @staticmethod
    def available() -> bool:
        return _docker_available()

    def evaluate(
        self,
        code: str,
        class_name: str,
        cases: Iterable[JavaFunctionalCase],
    ) -> Dict[str, Any]:
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
            # The public class's file name must match the class name exactly
            # -- javac rejects the compilation unit otherwise.
            candidate_path = root / f"{class_name}.java"
            candidate_path.write_text(code or "", encoding="utf-8")
            try:
                runner_source = _java_runner_source(cases, package_name=package_name)
            except ValueError as exc:
                return _summary([], "ERROR", str(exc))
            runner_path = root / "Runner.java"
            runner_path.write_text(runner_source, encoding="utf-8")
            root.chmod(0o755)
            for path in (candidate_path, runner_path):
                path.chmod(0o644)
            container_name = f"repocoder-func-eval-java-{uuid.uuid4().hex[:12]}"
            command = [
                "docker", "run", "--rm",
                *_isolation_flags(container_name, self.memory, self.cpus, "48m"),
                "-e", "HOME=/tmp",
                "-v", f"{root.resolve()}:/work:ro",
                self.image,
                "sh", "-c",
                # Compile into /tmp (writable) since /work is read-only;
                # javac's own errors go to stderr, which _run_docker/completed
                # already captures on a non-zero exit.
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
                    results.append(
                        FunctionalResult(case_id=case_id, status=status, passed=(status == "PASS"), detail=detail)
                    )
                if len(results) != len(cases):
                    return _summary(
                        results, "ERROR", f"expected {len(cases)} result lines, got {len(results)}"
                    )
            except ValueError as exc:
                return _summary([], "ERROR", f"invalid runner output: {exc}")
            return _summary(results, "COMPLETE", "")


def compare_functional_outputs(
    no_rag_code: str,
    rag_code: str,
    cases: Iterable[FunctionalCase],
    evaluator: Optional[DockerPythonEvaluator] = None,
) -> Dict[str, Any]:
    evaluator = evaluator or DockerPythonEvaluator()
    cases = list(cases)
    no_rag = evaluator.evaluate(extract_code(no_rag_code, "python"), cases)
    with_rag = evaluator.evaluate(extract_code(rag_code, "python"), cases)
    return {"no_rag": no_rag, "with_rag": with_rag, "pass_rate_lift": _pass_rate_lift(no_rag, with_rag)}


def compare_java_functional_outputs(
    no_rag_code: str,
    rag_code: str,
    class_name: str,
    cases: Iterable[JavaFunctionalCase],
    evaluator: Optional[DockerJavaEvaluator] = None,
) -> Dict[str, Any]:
    evaluator = evaluator or DockerJavaEvaluator()
    cases = list(cases)
    no_rag = evaluator.evaluate(extract_code(no_rag_code, "java"), class_name, cases)
    with_rag = evaluator.evaluate(extract_code(rag_code, "java"), class_name, cases)
    return {"no_rag": no_rag, "with_rag": with_rag, "pass_rate_lift": _pass_rate_lift(no_rag, with_rag)}


def _pass_rate_lift(no_rag: Dict[str, Any], with_rag: Dict[str, Any]) -> Optional[float]:
    no_rate = no_rag.get("pass_rate")
    rag_rate = with_rag.get("pass_rate")
    if isinstance(no_rate, (int, float)) and isinstance(rag_rate, (int, float)):
        return rag_rate - no_rate
    return None
