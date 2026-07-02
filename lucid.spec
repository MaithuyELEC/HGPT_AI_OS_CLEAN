# -*- mode: python ; coding: utf-8 -*-

from pathlib import Path

block_cipher = None

APP_NAME = "LUCID"
APP_BUNDLE = "LUCID.app"
ICON_ICNS = "assets/LUCID.icns" if Path("assets/LUCID.icns").exists() else None
ICON_ICO = "assets/LUCID.ico" if Path("assets/LUCID.ico").exists() else None

datas = [
    ("templates", "templates"),
    ("knowledge", "knowledge"),
    ("assets", "assets"),
    ("planner", "planner"),
    ("outputs", "outputs"),
    ("src/hgpt_ai_os/config", "hgpt_ai_os/config"),
]

a = Analysis(
    ['src/hgpt_ai_os/gui/app.py'],
    pathex=['src'],
    binaries=[],
    datas=datas,
    hiddenimports=[
        'PySide6',
        'PySide6.QtCore',
        'PySide6.QtGui',
        'PySide6.QtWidgets',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name=APP_NAME,
    console=False,
    icon=ICON_ICO,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=False,
    name=APP_NAME,
)

app = BUNDLE(
    coll,
    name=APP_BUNDLE,
    icon=ICON_ICNS,
    bundle_identifier="com.lucidauto.desktop",
    info_plist={
        "CFBundleShortVersionString": "1.0.0",
        "CFBundleVersion": "15",
    },
)