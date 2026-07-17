"""Tests for evaluation metrics and sandbox executor."""

import json
import subprocess
import sys
from pathlib import Path
from unittest.mock import patch

import pytest

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "evaluation"))
sys.path.insert(0, str(PROJECT_ROOT / "sandbox"))


class TestMetrics:
    def test_compute_bleu_identical(self):
        from metrics import compute_bleu
        preds = ["def add(a, b): return a + b"]
        refs = ["def add(a, b): return a + b"]
        result = compute_bleu(preds, refs)
        assert "bleu" in result
        assert result["bleu"] > 50

    def test_compute_bleu_different(self):
        from metrics import compute_bleu
        preds = ["x = 1"]
        refs = ["def foo(): pass"]
        result = compute_bleu(preds, refs)
        assert "bleu" in result
        assert result["bleu"] < 50

    def test_compute_codebleu_identical(self):
        from metrics import compute_codebleu
        code = "def add(a, b):\n    return a + b"
        result = compute_codebleu([code], [code])
        assert "codebleu" in result
        assert "error" not in result, (
            f"CodeBLEU failed — check tree-sitter pins (>=0.23.2) in requirements.txt: "
            f"{result.get('error')}"
        )
        assert result["codebleu"] > 0.5

    def test_compute_execution_accuracy(self):
        from metrics import compute_execution_accuracy
        results = [{"passed": True}, {"passed": False}, {"passed": True}]
        report = compute_execution_accuracy(results)
        assert report["passed"] == 2
        assert report["total"] == 3
        assert abs(report["execution_accuracy"] - 2 / 3) < 0.01

    def test_compute_execution_accuracy_empty(self):
        from metrics import compute_execution_accuracy
        report = compute_execution_accuracy([])
        assert report["execution_accuracy"] == 0.0
        assert report["total"] == 0

    def test_compute_output_match_accuracy_matching(self):
        from metrics import compute_output_match_accuracy
        pred = [{"passed": True, "stdout": "hello\n"}]
        ref = [{"passed": True, "stdout": "hello"}]
        report = compute_output_match_accuracy(pred, ref)
        assert report["output_matched"] == 1
        assert report["output_comparable"] == 1
        assert report["output_match_accuracy"] == 1.0

    def test_compute_output_match_accuracy_pred_fails(self):
        from metrics import compute_output_match_accuracy
        pred = [{"passed": False, "stdout": ""}]
        ref = [{"passed": True, "stdout": "hello"}]
        report = compute_output_match_accuracy(pred, ref)
        assert report["output_matched"] == 0
        assert report["output_comparable"] == 0
        assert report["output_match_accuracy"] == 0.0

    def test_compute_output_match_accuracy_different_stdout(self):
        from metrics import compute_output_match_accuracy
        pred = [{"passed": True, "stdout": "foo"}]
        ref = [{"passed": True, "stdout": "bar"}]
        report = compute_output_match_accuracy(pred, ref)
        assert report["output_matched"] == 0
        assert report["output_comparable"] == 1
        assert report["output_match_accuracy"] == 0.0

    def test_normalize_code(self):
        from metrics import normalize_code
        code = "x = 1  # comment\ny = 2"
        normalized = normalize_code(code)
        assert "#" not in normalized
        assert "x = 1" in normalized

    def test_compute_all_metrics_structure(self):
        from metrics import compute_all_metrics
        preds = ["def add(a, b): return a + b"]
        refs = ["def add(a, b): return a + b"]
        report = compute_all_metrics(preds, refs, skip_bert=True)
        assert "bleu" in report
        assert "codebleu" in report

    @pytest.mark.slow
    def test_compute_bert_score(self):
        from metrics import compute_bert_score
        preds = ["def add(a, b): return a + b"]
        refs = ["def add(a, b): return a + b"]
        result = compute_bert_score(preds, refs)
        assert "bertscore_f1" in result


class TestSandboxRunner:
    def test_run_simple_code(self):
        from runner import run_code
        result = run_code("print('hello')")
        assert result["passed"] is True
        assert "hello" in result["stdout"]

    def test_run_failing_code(self):
        from runner import run_code
        result = run_code("raise ValueError('fail')")
        assert result["passed"] is False
        assert result["error"] is not None

    def test_run_with_assertion_test(self):
        from runner import run_code
        code = "def add(a, b):\n    return a + b"
        test_cases = [{"assertion": "assert add(1, 2) == 3"}]
        result = run_code(code, test_cases)
        assert result["passed"] is True

    def test_runner_cli(self):
        runner_path = PROJECT_ROOT / "sandbox" / "runner.py"
        payload = json.dumps({"code": "print(42)", "timeout": 5})
        proc = subprocess.run(
            [sys.executable, str(runner_path)],
            input=payload,
            capture_output=True,
            text=True,
            timeout=15,
        )
        output = json.loads(proc.stdout.strip().split("\n")[-1])
        assert output["passed"] is True
        assert "42" in output["stdout"]


class TestCodeExecutor:
    def test_local_execution_fallback(self):
        from executor import CodeExecutor
        executor = CodeExecutor(use_docker=False)
        result = executor.execute("print('test')")
        assert result["passed"] is True

    def test_execute_with_syntax_error(self):
        from executor import CodeExecutor
        executor = CodeExecutor(use_docker=False)
        result = executor.execute("def broken(:")
        assert result["passed"] is False


class TestAvatarTcLoading:
    def test_load_avatar_tc_unshuffled_head(self):
        from run_baseline_qwen import load_avatar_tc

        unshuffled = load_avatar_tc("valid", max_samples=5, shuffle=False)
        shuffled = load_avatar_tc("valid", max_samples=5, shuffle=True, seed=42)
        assert len(unshuffled) == 5
        assert unshuffled[0]["java_code"] != shuffled[0]["java_code"] or any(
            u["java_code"] != s["java_code"]
            for u, s in zip(unshuffled, shuffled)
        )

    def test_load_avatar_tc_shuffle_reproducible(self):
        from run_baseline_qwen import load_avatar_tc

        first = load_avatar_tc("valid", max_samples=5, shuffle=True, seed=42)
        second = load_avatar_tc("valid", max_samples=5, shuffle=True, seed=42)
        assert first == second

    def test_pick_inspect_index_seeded(self):
        from run_baseline_qwen import pick_inspect_index

        assert pick_inspect_index(10, seed=42) == pick_inspect_index(10, seed=42)
        assert 0 <= pick_inspect_index(10, seed=42) < 10

    def test_pick_inspect_index_unseeded(self):
        from run_baseline_qwen import pick_inspect_index

        idx = pick_inspect_index(10, seed=None)
        assert 0 <= idx < 10
