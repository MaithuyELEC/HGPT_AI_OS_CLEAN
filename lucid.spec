# -*- mode: python ; coding: utf-8 -*-

from pathlib import Path
from PyInstaller.utils.hooks import collect_all, collect_data_files, collect_submodules

block_cipher = None

APP_NAME = "LUCID"
APP_BUNDLE = "Lucid AI Studio.app"
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
])

for path in sorted(Path("src/hgpt_ai_os/topic_engine").glob("*.json")):
    datas.append((str(path), "hgpt_ai_os/topic_engine"))
    

qt_datas, qt_binaries, qt_hiddenimports = collect_all("PySide6")
engineering_pipeline_hiddenimports = collect_submodules(
    "hgpt_ai_os.engineering_pipeline"
)
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
    hiddenimports=qt_hiddenimports + engineering_pipeline_hiddenimports,
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
        "CFBundleDisplayName": "Lucid AI Studio",
        "CFBundleName": "Lucid AI Studio",
        "CFBundleShortVersionString": APP_VERSION,
        "CFBundleVersion": APP_BUILD,
        "LSApplicationCategoryType": "public.app-category.productivity",
    },
)
