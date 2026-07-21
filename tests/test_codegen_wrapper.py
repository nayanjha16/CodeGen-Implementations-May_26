"""Tests for CodeGenModel's checkpoint-loading branch logic.

Regression coverage for the bug where any `adapter_path` was always treated
as a PEFT/LoRA adapter, which breaks for *full* fine-tune checkpoints (e.g.
Checkpoint 2's `rust_full` run) that were saved via plain
`model.save_pretrained()` and have no `adapter_config.json`. All heavy calls
(HF download, PEFT) are monkeypatched out so this runs with no network/GPU.
"""

from __future__ import annotations

import sys
import types
from pathlib import Path

import pytest


class _FakeHFModel:
    def __init__(self, source: str):
        self.source = source

    def to(self, device):
        return self

    def eval(self):
        return self

    def resize_token_embeddings(self, n):
        return None


class _FakeTokenizer:
    def __len__(self):
        return 100


@pytest.fixture(autouse=True)
def _patch_heavy_deps(monkeypatch):
    """Stub out torch/transformers/peft/tokenizer loading so __init__ only
    exercises our own branch-selection logic, not real model downloads (this
    sandbox has no torch/transformers/peft installed at all, and even where
    they are available we don't want to hit the network or GPU in a unit test)."""
    if "torch" not in sys.modules:
        fake_torch = types.ModuleType("torch")
        fake_torch.dtype = object
        fake_torch.float16 = "float16"
        fake_torch.float32 = "float32"
        fake_cuda = types.SimpleNamespace(is_available=lambda: False)
        fake_torch.cuda = fake_cuda

        def _inference_mode():
            def decorator(fn):
                return fn

            return decorator

        fake_torch.inference_mode = _inference_mode
        fake_torch.nn = types.SimpleNamespace(functional=types.SimpleNamespace(normalize=lambda *a, **k: None))
        monkeypatch.setitem(sys.modules, "torch", fake_torch)

    from_pretrained_calls: list[str] = []

    fake_transformers = types.ModuleType("transformers")

    class FakeAutoModelForCausalLM:
        @staticmethod
        def from_pretrained(name_or_path, torch_dtype=None):
            from_pretrained_calls.append(str(name_or_path))
            return _FakeHFModel(str(name_or_path))

    fake_transformers.AutoModelForCausalLM = FakeAutoModelForCausalLM
    monkeypatch.setitem(sys.modules, "transformers", fake_transformers)

    peft_calls: list[str] = []
    fake_peft = types.ModuleType("peft")

    class FakePeftModel:
        @staticmethod
        def from_pretrained(model, adapter_path):
            peft_calls.append(str(adapter_path))
            return _FakeHFModel(f"peft:{adapter_path}")

    fake_peft.PeftModel = FakePeftModel
    monkeypatch.setitem(sys.modules, "peft", fake_peft)

    fake_tok_module = types.ModuleType("codegen_rag.data.tokenizer_utils")
    fake_tok_module.load_tokenizer = lambda name: _FakeTokenizer()
    monkeypatch.setitem(sys.modules, "codegen_rag.data.tokenizer_utils", fake_tok_module)

    return {"from_pretrained_calls": from_pretrained_calls, "peft_calls": peft_calls}


def test_loads_base_model_when_no_adapter_path():
    from codegen_rag.models.codegen_wrapper import CodeGenModel

    model = CodeGenModel(model_name="Salesforce/codegen-350M-multi", device="cpu")
    assert model.model.source == "Salesforce/codegen-350M-multi"


def test_lora_checkpoint_with_adapter_config_uses_peft(tmp_path: Path, _patch_heavy_deps):
    from codegen_rag.models.codegen_wrapper import CodeGenModel

    adapter_dir = tmp_path / "lora_checkpoint"
    adapter_dir.mkdir()
    (adapter_dir / "adapter_config.json").write_text("{}", encoding="utf-8")

    model = CodeGenModel(
        model_name="Salesforce/codegen-350M-multi", adapter_path=adapter_dir, device="cpu"
    )
    assert _patch_heavy_deps["peft_calls"] == [str(adapter_dir)]
    assert model.model.source == f"peft:{adapter_dir}"


def test_full_finetune_checkpoint_without_adapter_config_loads_directly(
    tmp_path: Path, _patch_heavy_deps
):
    """Regression test: a full-finetune checkpoint dir (no adapter_config.json,
    just a normal model save) must be loaded via from_pretrained() directly,
    not routed through PeftModel.from_pretrained() (which used to raise
    HFValidationError / ValueError: Can't find 'adapter_config.json')."""
    from codegen_rag.models.codegen_wrapper import CodeGenModel

    full_ckpt_dir = tmp_path / "checkpoint-002200"
    full_ckpt_dir.mkdir()
    (full_ckpt_dir / "config.json").write_text("{}", encoding="utf-8")

    model = CodeGenModel(
        model_name="Salesforce/codegen-350M-multi", adapter_path=full_ckpt_dir, device="cpu"
    )
    assert _patch_heavy_deps["peft_calls"] == []
    assert model.model.source == str(full_ckpt_dir)


def test_missing_checkpoint_dir_raises_file_not_found(tmp_path: Path):
    from codegen_rag.models.codegen_wrapper import CodeGenModel

    missing = tmp_path / "does_not_exist"
    with pytest.raises(FileNotFoundError):
        CodeGenModel(model_name="Salesforce/codegen-350M-multi", adapter_path=missing, device="cpu")
