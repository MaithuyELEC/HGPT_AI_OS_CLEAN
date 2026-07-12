# -*- mode: python ; coding: utf-8 -*-

from pathlib import Path
from PyInstaller.utils.hooks import collect_all, collect_data_files

block_cipher = None

APP_NAME = "LUCID"
APP_BUNDLE = "LUCID.app"
ICON_ICNS = "assets/LUCID.icns" if Path("assets/LUCID.icns").exists() else None
ICON_ICO = "assets/LUCID.ico" if Path("assets/LUCID.ico").exists() else None
version_ns = {}
exec(Path("src/hgpt_ai_os/version.py").read_text(), version_ns)
APP_VERSION = version_ns["APP_VERSION"].removeprefix("v")
APP_BUILD = version_ns["APP_BUILD"].removeprefix("RC")

datas = []

if Path(".env").exists():
    datas.append((".env", "."))

datas.extend([
    ("templates", "templates"),
    ("knowledge", "knowledge"),
    ("assets", "assets"),
    ("planner", "planner"),
    ("outputs", "outputs"),
    ("src/hgpt_ai_os/config", "hgpt_ai_os/config"),
    ("src/hgpt_ai_os/topic_engine/failure_intelligence_library.json", "hgpt_ai_os/topic_engine"),
    ("src/hgpt_ai_os/topic_engine/topic_intelligence_profiles.json", "hgpt_ai_os/topic_engine"),
])
    

qt_datas, qt_binaries, qt_hiddenimports = collect_all("PySide6")
qt_datas += collect_data_files(
    "PySide6",
    includes=[
        "Qt/plugins/platforms/*",
        "Qt/plugins/styles/*",
        "Qt/plugins/imageformats/*",
        "Qt/plugins/iconengines/*",
    ],
)
a = Analysis(
    ['src/hgpt_ai_os/gui/app.py'],
    pathex=['src'],
    binaries=qt_binaries,
    datas=datas + qt_datas,
    hiddenimports=qt_hiddenimports,
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
        "CFBundleDisplayName": "LUCID AUTO",
        "CFBundleName": "LUCID AUTO",
        "CFBundleShortVersionString": APP_VERSION,
        "CFBundleVersion": APP_BUILD,
        "LSApplicationCategoryType": "public.app-category.productivity",
    },
)
