"""Tests for project path helpers."""

from src.utils.paths import resolve_results_run_dir


class TestResolveResultsRunDir:
    def test_creates_named_run_directory(self, tmp_path, monkeypatch):
        monkeypatch.setattr(
            "src.utils.paths.get_results_dir", lambda: tmp_path / "results"
        )

        run_dir = resolve_results_run_dir("spider_baseline")

        assert run_dir == tmp_path / "results" / "spider_baseline"
        assert run_dir.is_dir()

    def test_strips_json_suffix_from_legacy_name(self, tmp_path, monkeypatch):
        monkeypatch.setattr(
            "src.utils.paths.get_results_dir", lambda: tmp_path / "results"
        )

        run_dir = resolve_results_run_dir("spider_baseline_results.json")

        assert run_dir == tmp_path / "results" / "spider_baseline_results"
        assert run_dir.is_dir()
