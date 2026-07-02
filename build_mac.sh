#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT_DIR"

PYTHON_BIN="${PYTHON_BIN:-python3}"
if [ -x ".venv/bin/python" ]; then
    PYTHON_BIN=".venv/bin/python"
fi

APP_VERSION=$("$PYTHON_BIN" -c 'from pathlib import Path; ns = {}; exec(Path("src/hgpt_ai_os/version.py").read_text(), ns); print(ns["APP_VERSION"])')
APP_RELEASE=$("$PYTHON_BIN" -c 'from pathlib import Path; ns = {}; exec(Path("src/hgpt_ai_os/version.py").read_text(), ns); print(ns["APP_RELEASE"])')
DMG_NAME="LUCID-${APP_VERSION}.dmg"

"$PYTHON_BIN" scripts/ensure_release_icons.py
"$PYTHON_BIN" -m PyInstaller --clean --noconfirm lucid.spec

mkdir -p release/Mac release/Windows release/Installer release/ReleaseNotes
rm -rf release/Mac/LUCID.app
rm -rf release/Mac/dmg
cp -R dist/LUCID.app release/Mac/LUCID.app

mkdir -p release/Mac/dmg
cp -R release/Mac/LUCID.app release/Mac/dmg/LUCID.app
ln -s /Applications release/Mac/dmg/Applications
cp RELEASE_NOTES.md release/ReleaseNotes/RELEASE_NOTES.md

if command -v hdiutil >/dev/null 2>&1; then
    rm -f "release/Mac/${DMG_NAME}"
    hdiutil create \
        -volname "LUCID AUTO" \
        -srcfolder release/Mac/dmg \
        -ov \
        -format UDZO \
        "release/Mac/${DMG_NAME}"
fi

echo "macOS release ready: ${APP_RELEASE}"
echo "release/Mac/LUCID.app"
echo "release/Mac/${DMG_NAME}"
