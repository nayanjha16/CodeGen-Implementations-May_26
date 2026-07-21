"""One-call environment bootstrap for Colab and local runs.

``bootstrap_environment()`` is the single entry point every notebook calls
in its first cell. It:

1. Detects whether we're running on Google Colab.
2. Installs any missing pip packages from ``requirements.txt``.
3. Mounts Google Drive (Colab only) and creates the project folder structure
   under ``MyDrive/<drive_subdir>`` so runs, checkpoints, and logs survive
   session restarts.
4. Detects GPU availability and prints a short hardware summary.
5. Returns the resolved :class:`~codegen_rag.config.Settings` object with
   ``root_dir`` pointed at the persistent location.

No manual edits are required — every path in the rest of the codebase is
derived from the object this function returns.
"""

from __future__ import annotations

import importlib
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

from codegen_rag.config import Settings, load_settings
from codegen_rag.utils.logging_config import configure_logging, get_logger
from codegen_rag.utils.seed import set_global_seed

logger = get_logger(__name__)


def is_colab() -> bool:
    return importlib.util.find_spec("google.colab") is not None


@dataclass
class HardwareInfo:
    has_gpu: bool
    device_name: str
    total_memory_gb: float
    cuda_version: str | None


def detect_hardware() -> HardwareInfo:
    try:
        import torch

        if torch.cuda.is_available():
            props = torch.cuda.get_device_properties(0)
            return HardwareInfo(
                has_gpu=True,
                device_name=props.name,
                total_memory_gb=round(props.total_memory / (1024**3), 2),
                cuda_version=torch.version.cuda,
            )
    except ImportError:
        pass
    return HardwareInfo(has_gpu=False, device_name="cpu", total_memory_gb=0.0, cuda_version=None)


def install_requirements(requirements_path: Path, quiet: bool = True) -> None:
    """Install any missing packages. No-op locally if already satisfied."""
    if not requirements_path.exists():
        logger.warning("requirements.txt not found at %s, skipping install", requirements_path)
        return
    cmd = [sys.executable, "-m", "pip", "install", "-r", str(requirements_path)]
    if quiet:
        cmd.append("-q")
    logger.info("Installing dependencies from %s ...", requirements_path)
    subprocess.run(cmd, check=True)
    _remove_incompatible_preinstalled_packages(quiet=quiet)


def _remove_incompatible_preinstalled_packages(quiet: bool = True) -> None:
    """Strip out Colab-preinstalled packages known to break our stack.

    torchao ships preinstalled on some Colab images at a version too old
    for current peft releases, which raises ImportError the moment peft
    is imported (even though this project never uses torchao's
    quantization features at all). Uninstalling it, if present, sidesteps
    the check entirely. Safe to run even when torchao isn\'t installed.
    """
    result = subprocess.run(
        [sys.executable, "-m", "pip", "show", "torchao"], capture_output=True, text=True
    )
    if result.returncode != 0:
        return

    logger.info("Removing preinstalled torchao (incompatible with current peft on Colab)")
    cmd = [sys.executable, "-m", "pip", "uninstall", "-y", "torchao"]
    if quiet:
        cmd.append("-q")
    subprocess.run(cmd, check=False)
    _remove_incompatible_preinstalled_packages(quiet=quiet)


def _remove_incompatible_preinstalled_packages(quiet: bool = True) -> None:
    """Strip out Colab-preinstalled packages known to break our stack.

    torchao ships preinstalled on some Colab images at a version too old
    for current peft releases, which raises ImportError the moment peft
    is imported (even though this project never uses torchao's
    quantization features at all). Uninstalling it, if present, sidesteps
    the check entirely. Safe to run even when torchao isn\'t installed.
    """
    result = subprocess.run(
        [sys.executable, "-m", "pip", "show", "torchao"], capture_output=True, text=True
    )
    if result.returncode != 0:
        return

    logger.info("Removing preinstalled torchao (incompatible with current peft on Colab)")
    cmd = [sys.executable, "-m", "pip", "uninstall", "-y", "torchao"]
    if quiet:
        cmd.append("-q")
    subprocess.run(cmd, check=False)
    _remove_incompatible_preinstalled_packages(quiet=quiet)


def _remove_incompatible_preinstalled_packages(quiet: bool = True) -> None:
    """Strip out Colab-preinstalled packages known to break our stack.

    torchao ships preinstalled on some Colab images at a version too old
    for current peft releases, which raises ImportError the moment peft
    is imported (even though this project never uses torchao's
    quantization features at all). Uninstalling it, if present, sidesteps
    the check entirely. Safe to run even when torchao isn\'t installed.
    """
    result = subprocess.run(
        [sys.executable, "-m", "pip", "show", "torchao"], capture_output=True, text=True
    )
    if result.returncode != 0:
        return

    logger.info("Removing preinstalled torchao (incompatible with current peft on Colab)")
    cmd = [sys.executable, "-m", "pip", "uninstall", "-y", "torchao"]
    if quiet:
        cmd.append("-q")
    subprocess.run(cmd, check=False)
    _remove_incompatible_preinstalled_packages(quiet=quiet)


def _remove_incompatible_preinstalled_packages(quiet: bool = True) -> None:
    """Strip out Colab-preinstalled packages known to break our stack.

    torchao ships preinstalled on some Colab images at a version too old
    for current peft releases, which raises ImportError the moment peft
    is imported (even though this project never uses torchao's
    quantization features at all). Uninstalling it, if present, sidesteps
    the check entirely. Safe to run even when torchao isn\'t installed.
    """
    result = subprocess.run(
        [sys.executable, "-m", "pip", "show", "torchao"], capture_output=True, text=True
    )
    if result.returncode != 0:
        return

    logger.info("Removing preinstalled torchao (incompatible with current peft on Colab)")
    cmd = [sys.executable, "-m", "pip", "uninstall", "-y", "torchao"]
    if quiet:
        cmd.append("-q")
    subprocess.run(cmd, check=False)
    _remove_incompatible_preinstalled_packages(quiet=quiet)


def _remove_incompatible_preinstalled_packages(quiet: bool = True) -> None:
    """Strip out Colab-preinstalled packages known to break our stack.

    torchao ships preinstalled on some Colab images at a version too old
    for current peft releases, which raises ImportError the moment peft
    is imported (even though this project never uses torchao's
    quantization features at all). Uninstalling it, if present, sidesteps
    the check entirely. Safe to run even when torchao isn\'t installed.
    """
    result = subprocess.run(
        [sys.executable, "-m", "pip", "show", "torchao"], capture_output=True, text=True
    )
    if result.returncode != 0:
        return

    logger.info("Removing preinstalled torchao (incompatible with current peft on Colab)")
    cmd = [sys.executable, "-m", "pip", "uninstall", "-y", "torchao"]
    if quiet:
        cmd.append("-q")
    subprocess.run(cmd, check=False)
    _remove_incompatible_preinstalled_packages(quiet=quiet)


def _remove_incompatible_preinstalled_packages(quiet: bool = True) -> None:
    """Strip out Colab-preinstalled packages known to break our stack.

    torchao ships preinstalled on some Colab images at a version too old
    for current peft releases, which raises ImportError the moment peft
    is imported (even though this project never uses torchao's
    quantization features at all). Uninstalling it, if present, sidesteps
    the check entirely. Safe to run even when torchao isn\'t installed.
    """
    result = subprocess.run(
        [sys.executable, "-m", "pip", "show", "torchao"], capture_output=True, text=True
    )
    if result.returncode != 0:
        return

    logger.info("Removing preinstalled torchao (incompatible with current peft on Colab)")
    cmd = [sys.executable, "-m", "pip", "uninstall", "-y", "torchao"]
    if quiet:
        cmd.append("-q")
    subprocess.run(cmd, check=False)


def mount_drive_and_relocate(drive_subdir: str) -> Path:
    """Mount Google Drive on Colab and return the persistent project directory.

    Falls back to the current working directory when not on Colab.
    """
    if not is_colab():
        return Path.cwd()

    from google.colab import drive  # type: ignore

    mount_point = Path("/content/drive")
    if not mount_point.exists():
        drive.mount(str(mount_point))

    persistent_root = mount_point / "MyDrive" / drive_subdir
    persistent_root.mkdir(parents=True, exist_ok=True)
    logger.info("Google Drive mounted. Project root: %s", persistent_root)
    return persistent_root


def create_folder_structure(root: Path, settings: Settings) -> None:
    for key in ("data_raw", "data_processed", "data_interim", "checkpoints", "logs", "results", "faiss_index"):
        relative = getattr(settings.paths, key)
        (root / relative).mkdir(parents=True, exist_ok=True)
    logger.info("Folder structure ready under %s", root)


def bootstrap_environment(
    install_deps: bool = True,
    mount_drive: bool = True,
    seed: int | None = None,
) -> Settings:
    """Run the full Colab/local bootstrap sequence and return resolved Settings."""
    settings = load_settings()

    if install_deps:
        install_requirements(settings.root_dir / "requirements.txt")

    if mount_drive and is_colab():
        persistent_root = mount_drive_and_relocate(settings.project.drive_subdir)
        object.__setattr__(settings, "root_dir", persistent_root)

    create_folder_structure(settings.root_dir, settings)

    configure_logging(
        log_dir=settings.path_for("logs"),
        level=settings.logging.level,
        log_to_file=settings.logging.log_to_file,
    )

    set_global_seed(seed if seed is not None else settings.project.seed)

    hw = detect_hardware()
    logger.info(
        "Environment ready | Colab=%s | GPU=%s (%s, %.1f GB) | CUDA=%s | root=%s",
        is_colab(),
        hw.has_gpu,
        hw.device_name,
        hw.total_memory_gb,
        hw.cuda_version,
        settings.root_dir,
    )
    if not hw.has_gpu:
        logger.warning(
            "No GPU detected. Training steps will fall back to CPU and will be "
            "slow — in Colab, use Runtime > Change runtime type > GPU."
        )
    return settings
