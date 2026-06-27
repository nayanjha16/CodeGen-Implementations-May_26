"""Tests for device resolution helpers."""

from __future__ import annotations

from unittest.mock import patch

from src.utils.device import (
    is_cpu_device,
    is_directml_device,
    normalize_device_request,
    resolve_device,
    supports_dataloader_pin_memory,
)


def test_resolve_device_auto_prefers_cuda():
    with patch("torch.cuda.is_available", return_value=True):
        assert resolve_device("auto") == "cuda"


def test_resolve_device_auto_prefers_mps_when_no_cuda():
    with patch("torch.cuda.is_available", return_value=False), patch(
        "torch.backends.mps.is_available",
        return_value=True,
    ):
        assert resolve_device("auto") == "mps"


def test_resolve_device_auto_uses_directml_when_available():
    with patch("torch.cuda.is_available", return_value=False), patch(
        "torch.backends.mps.is_available",
        return_value=False,
    ), patch("src.utils.device.directml_available", return_value=True), patch(
        "src.utils.device.resolve_directml_device",
        return_value="privateuseone:0",
    ):
        assert resolve_device("auto") == "privateuseone:0"


def test_normalize_device_request_maps_dml_alias():
    with patch("src.utils.device.directml_available", return_value=True), patch(
        "src.utils.device.resolve_directml_device",
        return_value="privateuseone:0",
    ):
        assert normalize_device_request("dml") == "privateuseone:0"
        assert normalize_device_request("directml") == "privateuseone:0"


def test_normalize_device_request_falls_back_to_cpu_without_directml():
    with patch("src.utils.device.directml_available", return_value=False):
        assert normalize_device_request("dml") == "cpu"


def test_is_directml_device():
    assert is_directml_device("privateuseone:0")
    assert not is_directml_device("cuda")
    assert not is_directml_device("cpu")


def test_is_cpu_device():
    assert is_cpu_device("cpu")
    assert not is_cpu_device("cuda")


def test_supports_dataloader_pin_memory():
    assert supports_dataloader_pin_memory("cuda")
    assert supports_dataloader_pin_memory("cuda:0")
    assert not supports_dataloader_pin_memory("mps")
    assert not supports_dataloader_pin_memory("privateuseone:0")
