"""Tests for device resolution helpers."""

from __future__ import annotations

import unittest
from unittest.mock import patch

from src.utils.device import (
    is_cpu_device,
    is_directml_device,
    normalize_device_request,
    resolve_device,
    supports_dataloader_pin_memory,
)


class DeviceTest(unittest.TestCase):
    def test_resolve_device_auto_prefers_cuda(self) -> None:
        with patch("torch.cuda.is_available", return_value=True):
            self.assertEqual(resolve_device("auto"), "cuda")

    def test_resolve_device_auto_prefers_mps_when_no_cuda(self) -> None:
        with patch("torch.cuda.is_available", return_value=False), patch(
            "torch.backends.mps.is_available",
            return_value=True,
        ):
            self.assertEqual(resolve_device("auto"), "mps")

    def test_resolve_device_auto_uses_directml_when_available(self) -> None:
        with patch("torch.cuda.is_available", return_value=False), patch(
            "torch.backends.mps.is_available",
            return_value=False,
        ), patch("src.utils.device.directml_available", return_value=True), patch(
            "src.utils.device.resolve_directml_device",
            return_value="privateuseone:0",
        ):
            self.assertEqual(resolve_device("auto"), "privateuseone:0")

    def test_normalize_device_request_maps_dml_alias(self) -> None:
        with patch("src.utils.device.directml_available", return_value=True), patch(
            "src.utils.device.resolve_directml_device",
            return_value="privateuseone:0",
        ):
            self.assertEqual(normalize_device_request("dml"), "privateuseone:0")
            self.assertEqual(normalize_device_request("directml"), "privateuseone:0")

    def test_normalize_device_request_falls_back_to_cpu_without_directml(self) -> None:
        with patch("src.utils.device.directml_available", return_value=False):
            self.assertEqual(normalize_device_request("dml"), "cpu")

    def test_is_directml_device(self) -> None:
        self.assertTrue(is_directml_device("privateuseone:0"))
        self.assertFalse(is_directml_device("cuda"))
        self.assertFalse(is_directml_device("cpu"))

    def test_is_cpu_device(self) -> None:
        self.assertTrue(is_cpu_device("cpu"))
        self.assertFalse(is_cpu_device("cuda"))

    def test_supports_dataloader_pin_memory(self) -> None:
        self.assertTrue(supports_dataloader_pin_memory("cuda"))
        self.assertTrue(supports_dataloader_pin_memory("cuda:0"))
        self.assertFalse(supports_dataloader_pin_memory("mps"))
        self.assertFalse(supports_dataloader_pin_memory("privateuseone:0"))


if __name__ == "__main__":
    unittest.main()
