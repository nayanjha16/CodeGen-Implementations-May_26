"""Tests for MPS/CUDA/CPU device selection."""

import sys
from pathlib import Path
from unittest.mock import patch

import pytest

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from utils.device import (
    apply_mac_training_overrides,
    get_best_device,
    get_inference_dtype,
    get_training_precision,
)


class TestDeviceSelection:
    def test_cpu_fallback(self):
        with patch("utils.device.torch.cuda.is_available", return_value=False), \
             patch("utils.device.is_mps_available", return_value=False):
            assert get_best_device() == "cpu"

    def test_mps_priority_over_cpu(self):
        with patch("utils.device.torch.cuda.is_available", return_value=False), \
             patch("utils.device.is_mps_available", return_value=True):
            assert get_best_device() == "mps"

    def test_cuda_priority_over_mps(self):
        with patch("utils.device.torch.cuda.is_available", return_value=True), \
             patch("utils.device.is_mps_available", return_value=True):
            assert get_best_device() == "cuda"

    def test_explicit_mps_request_raises_when_unavailable(self):
        with patch("utils.device.is_mps_available", return_value=False):
            with pytest.raises(RuntimeError, match="MPS"):
                get_best_device("mps")

    def test_mps_training_disables_fp16(self):
        precision = get_training_precision("mps")
        assert precision["fp16"] is False

    def test_cuda_training_enables_fp16(self):
        precision = get_training_precision("cuda")
        assert precision["fp16"] is True

    def test_mps_inference_dtype_is_float32_or_bfloat16(self):
        import torch
        dtype = get_inference_dtype("mps")
        assert dtype in (torch.float32, torch.bfloat16)

    def test_mac_training_overrides_reduce_batch_size(self):
        config = {
            "per_device_train_batch_size": 8,
            "per_device_eval_batch_size": 8,
            "gradient_accumulation_steps": 4,
            "fp16": True,
        }
        updated = apply_mac_training_overrides(config, "mps")
        assert updated["per_device_train_batch_size"] == 4
        assert updated["fp16"] is False
        assert updated["gradient_accumulation_steps"] >= 8
