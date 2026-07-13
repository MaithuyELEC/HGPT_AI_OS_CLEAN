from __future__ import annotations

import sys
from pathlib import Path


def resource_root() -> Path:
    if getattr(sys, "frozen", False):
        meipass = Path(sys._MEIPASS)
        resources = meipass.parent / "Resources"
        if resources.exists():
            return resources
        return meipass

    return Path(__file__).resolve().parents[3]


def resource_path(relative: str) -> Path:
    base = resource_root()
    path = base / relative
    if path.exists():
        return path

    if not getattr(sys, "frozen", False):
        src_path = base / "src" / relative
        if src_path.exists():
            return src_path

    return path
