"""macOS-specific desktop integration."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any


def set_dock_name(name: str) -> None:
    """Set the process name used by macOS for Dock hover and Activity Monitor."""
    if sys.platform != "darwin" or not name.strip():
        return

    try:
        from Foundation import NSBundle, NSProcessInfo

        NSProcessInfo.processInfo().setProcessName_(name)

        bundle = NSBundle.mainBundle()
        info = bundle.localizedInfoDictionary() if bundle else None
        if info is None and bundle is not None:
            info = bundle.infoDictionary()
        if info is not None:
            info["CFBundleName"] = name
            info["CFBundleDisplayName"] = name
    except ImportError:
        pass


def set_dock_icon(logo_path: Path) -> None:
    """Set the Dock icon when running outside a bundled .app."""
    if sys.platform != "darwin" or not logo_path.exists():
        return

    try:
        from AppKit import NSApplication, NSImage

        image = NSImage.alloc().initWithContentsOfFile_(str(logo_path))
        if image is not None:
            NSApplication.sharedApplication().setApplicationIconImage_(image)
    except ImportError:
        pass


def set_tk_app_name(root: Any, name: str) -> None:
    """Set the Tk application name used by macOS windowing integration."""
    if sys.platform != "darwin" or not name.strip():
        return

    try:
        root.call("tk", "appname", name)
    except Exception:
        pass
