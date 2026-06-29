# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['src/hgpt_ai_os/gui/app.py'],
    pathex=['src'],
    binaries=[],
    datas=[
    ("templates", "templates"),
    ("knowledge", "knowledge"),
    ("planner", "planner"),
],
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
    name='LUCID',
    console=False,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=False,
    name='LUCID',
)

app = BUNDLE(
    coll,
    name='LUCID.app',
)