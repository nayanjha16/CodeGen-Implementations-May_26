from __future__ import annotations

import json
import sys
import types
from pathlib import Path

import pytest

from codegen_rag.api.dependencies import (
    AppState,
    _best_checkpoint_dir,
    describe_available_checkpoints,
    get_codegen_model,
)
from codegen_rag.config import Settings


def _settings(tmp_path: Path) -> Settings:
    return Settings(root_dir=tmp_path)


def _write_checkpoint(run_dir: Path, step: int, marker: str = "config.json") -> Path:
    """Create a nested `checkpoint-NNNNNN` dir the way CheckpointManager.save()
    actually does, with either `config.json` (full fine-tune) or
    `adapter_config.json` (LoRA) as the marker file."""
    ckpt_dir = run_dir / f"checkpoint-{step:06d}"
    ckpt_dir.mkdir(parents=True, exist_ok=True)
    (ckpt_dir / marker).write_text("{}")
    return ckpt_dir


def _write_training_state(run_dir: Path, best_checkpoint_dir: Path) -> None:
    state = {"best": {"checkpoint_dir": str(best_checkpoint_dir)}, "latest": {}}
    (run_dir / "training_state.json").write_text(json.dumps(state))


class FakeFineTunedModel:
    """Stand-in for CodeGenModel that records how it was constructed."""

    def __init__(self, model_name: str, adapter_path=None, device=None):  # noqa: ANN001
        self.model_name = model_name
        self.adapter_path = adapter_path


@pytest.fixture
def fake_wrapper_module(monkeypatch):
    """Swap in a fake `codegen_rag.models.codegen_wrapper` module so
    `get_codegen_model`'s lazy `from codegen_rag.models.codegen_wrapper
    import load_model_for_task` never touches the real (torch-requiring)
    module -- this sandbox has no torch installed, and even where it is
    available a unit test shouldn't load a real model.

    Returns the list of `adapter_path` values each fake call was made with.
    """
    calls: list[Path | None] = []

    def fake_load(settings, adapter_path=None):  # noqa: ANN001
        calls.append(adapter_path)
        return FakeFineTunedModel(settings.base_model.name, adapter_path)

    fake_module = types.ModuleType("codegen_rag.models.codegen_wrapper")
    fake_module.load_model_for_task = fake_load
    monkeypatch.setitem(sys.modules, "codegen_rag.models.codegen_wrapper", fake_module)
    return calls


def test_best_checkpoint_dir_prefers_full_over_lora_subset(tmp_path: Path):
    settings = _settings(tmp_path)
    checkpoints = settings.path_for("checkpoints")
    full_ckpt = _write_checkpoint(checkpoints / "rust_full", 3000, marker="config.json")
    _write_checkpoint(checkpoints / "rust_lora_subset", 252, marker="adapter_config.json")

    result = _best_checkpoint_dir(settings, "rust")
    assert result == full_ckpt


def test_best_checkpoint_dir_falls_back_to_lora_subset(tmp_path: Path):
    settings = _settings(tmp_path)
    checkpoints = settings.path_for("checkpoints")
    lora_ckpt = _write_checkpoint(checkpoints / "rust_lora_subset", 252, marker="adapter_config.json")

    result = _best_checkpoint_dir(settings, "rust")
    assert result == lora_ckpt


def test_best_checkpoint_dir_none_when_nothing_trained_yet(tmp_path: Path):
    settings = _settings(tmp_path)
    assert _best_checkpoint_dir(settings, "rust") is None


def test_best_checkpoint_dir_none_for_language_without_finetuning_task(tmp_path: Path):
    settings = _settings(tmp_path)
    checkpoints = settings.path_for("checkpoints")
    # Even if a directory happens to exist under this name, "python" isn't a
    # language this project ever fine-tunes -- only Rust (proposal's Task 4).
    _write_checkpoint(checkpoints / "python_full", 100, marker="config.json")
    assert _best_checkpoint_dir(settings, "python") is None


def test_best_checkpoint_dir_skips_empty_run_directory(tmp_path: Path):
    settings = _settings(tmp_path)
    checkpoints = settings.path_for("checkpoints")
    # rust_full exists but has no checkpoint-* subdirs yet (e.g. training
    # started but never hit a save_steps boundary, or a Colab disconnect
    # happened before the first save) -- should fall through to
    # rust_lora_subset, not error.
    (checkpoints / "rust_full").mkdir()
    lora_ckpt = _write_checkpoint(checkpoints / "rust_lora_subset", 252, marker="adapter_config.json")

    result = _best_checkpoint_dir(settings, "rust")
    assert result == lora_ckpt


def test_best_checkpoint_dir_picks_highest_numbered_checkpoint_without_training_state(tmp_path: Path):
    """Mirrors the real bug this project hit: CheckpointManager nests saves
    under checkpoint-NNNNNN subdirectories (not directly in the run dir), and
    without a readable training_state.json we should pick the most-trained
    (highest step) one rather than reporting no checkpoint at all."""
    settings = _settings(tmp_path)
    checkpoints = settings.path_for("checkpoints")
    _write_checkpoint(checkpoints / "rust_full", 2200)
    _write_checkpoint(checkpoints / "rust_full", 2800)
    latest = _write_checkpoint(checkpoints / "rust_full", 3000)

    result = _best_checkpoint_dir(settings, "rust")
    assert result == latest


def test_best_checkpoint_dir_prefers_training_state_best_pointer(tmp_path: Path):
    """When training_state.json records a `best` (lowest-loss) checkpoint
    that differs from the highest step number, prefer that recorded best."""
    settings = _settings(tmp_path)
    run_dir = settings.path_for("checkpoints") / "rust_lora_subset"
    _write_checkpoint(run_dir, 250, marker="adapter_config.json")
    best = _write_checkpoint(run_dir, 252, marker="adapter_config.json")
    _write_training_state(run_dir, best)

    result = _best_checkpoint_dir(settings, "rust")
    assert result == best


def test_best_checkpoint_dir_falls_back_to_flat_layout(tmp_path: Path):
    """Older/manually-placed checkpoints that aren't nested under
    checkpoint-NNNNNN (i.e. the marker file sits directly in the run dir)
    should still be picked up as a last resort."""
    settings = _settings(tmp_path)
    run_dir = settings.path_for("checkpoints") / "rust_full"
    run_dir.mkdir(parents=True)
    (run_dir / "config.json").write_text("{}")

    result = _best_checkpoint_dir(settings, "rust")
    assert result == run_dir


def test_describe_available_checkpoints_reports_none_when_untrained(tmp_path: Path):
    settings = _settings(tmp_path)
    assert describe_available_checkpoints(settings) == {"rust": None}


def test_describe_available_checkpoints_reports_resolved_path(tmp_path: Path):
    settings = _settings(tmp_path)
    checkpoints = settings.path_for("checkpoints")
    ckpt = _write_checkpoint(checkpoints / "rust_full", 3000)

    result = describe_available_checkpoints(settings)
    assert result == {"rust": str(ckpt)}


def test_get_codegen_model_falls_back_to_base_singleton_without_checkpoint(tmp_path: Path, fake_wrapper_module):
    state = AppState(settings=_settings(tmp_path))
    model = get_codegen_model(state, language="python")
    assert isinstance(model, FakeFineTunedModel)
    assert model.adapter_path is None
    assert state.model is model
    assert state.active_checkpoints["python"] is None
    assert state.language_models == {}


def test_get_codegen_model_loads_and_caches_finetuned_checkpoint_for_rust(tmp_path: Path, fake_wrapper_module):
    settings = _settings(tmp_path)
    checkpoints = settings.path_for("checkpoints")
    ckpt = _write_checkpoint(checkpoints / "rust_full", 3000)

    state = AppState(settings=settings)
    model = get_codegen_model(state, language="rust")

    assert isinstance(model, FakeFineTunedModel)
    assert model.adapter_path == ckpt
    assert state.active_checkpoints["rust"] == str(ckpt)
    assert state.model is None  # base singleton untouched

    # Second call for the same language must reuse the cached instance, not
    # reload the checkpoint from disk again.
    model_again = get_codegen_model(state, language="rust")
    assert model_again is model
    assert len(fake_wrapper_module) == 1


def test_get_codegen_model_defaults_to_python_when_language_omitted(tmp_path: Path, fake_wrapper_module):
    state = AppState(settings=_settings(tmp_path))
    model = get_codegen_model(state)
    assert model.adapter_path is None
