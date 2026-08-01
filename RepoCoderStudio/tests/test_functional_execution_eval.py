from src.functional_execution_eval import (
    DockerJavaEvaluator,
    DockerPythonEvaluator,
    FunctionalCase,
    JavaFunctionalCase,
    _java_package_name,
    _java_runner_source,
    compare_functional_outputs,
    compare_java_functional_outputs,
)


def test_functional_evaluator_fails_closed_without_docker(monkeypatch):
    monkeypatch.setattr(DockerPythonEvaluator, "available", staticmethod(lambda: False))
    evaluator = DockerPythonEvaluator()
    result = evaluator.evaluate(
        "def add(a, b): return a + b",
        [FunctionalCase("add", "add", [1, 2], {}, 3)],
    )
    assert result["status"] == "NOT_FEASIBLE"
    assert result["cases_run"] == 0
    assert result["execution_isolated"] is False


def test_java_functional_evaluator_fails_closed_without_docker(monkeypatch):
    monkeypatch.setattr(DockerJavaEvaluator, "available", staticmethod(lambda: False))
    evaluator = DockerJavaEvaluator()
    result = evaluator.evaluate(
        "public class Flag { public boolean isTrue() { return true; } }",
        "Flag",
        [JavaFunctionalCase("case1", "Flag", "isTrue", [], "true")],
    )
    assert result["status"] == "NOT_FEASIBLE"
    assert result["cases_run"] == 0
    assert result["execution_isolated"] is False


def test_java_runner_source_generates_one_try_block_per_case():
    cases = [
        JavaFunctionalCase("pan_ok", "KycValidator", "validatePan", ['"ABCDE1234F"'], "true"),
        JavaFunctionalCase("mask", "KycValidator", "maskPan", ['"abcde1234f"'], '"******234F"'),
    ]
    source = _java_runner_source(cases)
    assert "public class Runner" in source
    assert source.count("try {") == 2
    assert "new KycValidator().validatePan(\"ABCDE1234F\")" in source
    assert "new KycValidator().maskPan(\"abcde1234f\")" in source
    assert 'out.append("pan_ok|"' in source
    assert 'out.append("mask|"' in source


def test_java_runner_source_uses_candidate_package():
    assert _java_package_name(
        "package transactions;\npublic class FraudDetector {}"
    ) == "transactions"
    source = _java_runner_source(
        [
            JavaFunctionalCase(
                "flag",
                "FraudDetector",
                "flagSuspiciousTransaction",
                ["70.0", "70.0"],
                "true",
            )
        ],
        package_name="transactions",
    )
    assert source.startswith("package transactions;")
    assert "new FraudDetector().flagSuspiciousTransaction(70.0, 70.0)" in source


class _RecordingPythonEvaluator:
    def __init__(self):
        self.codes = []

    def evaluate(self, code, cases):
        self.codes.append(code)
        return {"pass_rate": 1.0}


class _RecordingJavaEvaluator:
    def __init__(self):
        self.codes = []

    def evaluate(self, code, class_name, cases):
        self.codes.append(code)
        return {"pass_rate": 1.0}


def test_compare_helpers_extract_fenced_generated_code():
    python_evaluator = _RecordingPythonEvaluator()
    compare_functional_outputs(
        "```python\ndef answer(): return 1\n```",
        "```python\ndef answer(): return 2\n```",
        [],
        evaluator=python_evaluator,
    )
    assert python_evaluator.codes == [
        "def answer(): return 1",
        "def answer(): return 2",
    ]

    java_evaluator = _RecordingJavaEvaluator()
    compare_java_functional_outputs(
        "```java\npublic class Answer {}\n```",
        "```java\npublic class Answer { }\n```",
        "Answer",
        [],
        evaluator=java_evaluator,
    )
    assert java_evaluator.codes == [
        "public class Answer {}",
        "public class Answer { }",
    ]
