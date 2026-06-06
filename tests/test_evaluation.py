"""Tests for evaluation framework."""

from evaluation.metrics import EvaluationMetrics
from evaluation.mlflow_tracker import MLflowTracker


class TestEvaluationMetrics:
    def setup_method(self):
        self.metrics = EvaluationMetrics()

    def test_exact_match(self):
        assert self.metrics.exact_match(
            "SELECT name FROM students",
            "select name from students",
        )

    def test_exact_match_batch(self):
        preds = ["SELECT * FROM t", "SELECT name FROM t"]
        refs = ["SELECT * FROM t", "SELECT id FROM t"]
        acc = self.metrics.exact_match_batch(preds, refs)
        assert acc == 0.5

    def test_syntax_validity(self):
        preds = ["SELECT name FROM students", "INVALID QUERY"]
        rate = self.metrics.syntax_validity_rate(preds)
        assert 0 < rate < 1

    def test_execution_accuracy(self, sample_db):
        preds = ["SELECT name FROM students WHERE age > 20"]
        refs = ["SELECT name FROM students WHERE age > 20"]
        db_paths = [str(sample_db)]
        acc = self.metrics.execution_accuracy(preds, refs, db_paths)
        assert acc == 1.0

    def test_evaluate_all(self):
        preds = ["SELECT name FROM students WHERE age > 20"]
        refs = ["SELECT name FROM students WHERE age > 20"]
        result = self.metrics.evaluate_all(preds, refs)
        assert "exact_match" in result
        assert "bleu" in result
        assert "codebleu" in result


class TestMLflowTracker:
    def test_log_evaluation(self, tmp_path):
        tracker = MLflowTracker(
            experiment_name="test-experiment",
            tracking_uri=str(tmp_path / "mlruns"),
        )
        run_id = tracker.log_evaluation(
            model_name="test-model",
            dataset="test-dataset",
            prompt_template="default",
            metrics={
                "bleu": 0.5,
                "exact_match": 0.3,
                "codebleu": 0.4,
            },
        )
        assert run_id is not None
