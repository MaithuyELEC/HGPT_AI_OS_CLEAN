from __future__ import annotations

import sys
from pathlib import Path

from PySide6.QtGui import QIcon


APP_DISPLAY_NAME = "Lucid AI Studio"
APP_ORGANIZATION = "MaithuyELEC"
APP_POWERED_BY = "Powered by MaithuyELEC"


def bundled_asset_path(filename: str) -> Path:
    bundle_root = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parents[3]))
    return bundle_root / "assets" / filename


def app_icon() -> QIcon:
    for filename in ("LUCID.ico", "LUCID.icns", "LUCID.png"):
        path = bundled_asset_path(filename)
        if path.exists():
            icon = QIcon(str(path))
            if not icon.isNull():
                return icon
    return QIcon()
