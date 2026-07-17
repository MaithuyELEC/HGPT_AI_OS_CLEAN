#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT_DIR"

export PYINSTALLER_CONFIG_DIR="${PYINSTALLER_CONFIG_DIR:-$ROOT_DIR/work/pyinstaller-config}"
mkdir -p "$PYINSTALLER_CONFIG_DIR"

PYTHON_BIN="${PYTHON_BIN:-python3}"
if [ -x ".venv/bin/python" ]; then
    PYTHON_BIN=".venv/bin/python"
fi

APP_VERSION=$("$PYTHON_BIN" -c 'from pathlib import Path; ns = {}; exec(Path("src/hgpt_ai_os/version.py").read_text(), ns); print(ns["APP_VERSION"])')
APP_RELEASE=$("$PYTHON_BIN" -c 'from pathlib import Path; ns = {}; exec(Path("src/hgpt_ai_os/version.py").read_text(), ns); print(ns["APP_RELEASE"])')
DMG_NAME="Lucid-AI-Studio-${APP_VERSION}.dmg"
APP_BUNDLE="Lucid AI Studio.app"

"$PYTHON_BIN" scripts/ensure_release_icons.py
"$PYTHON_BIN" -m PyInstaller --clean --noconfirm lucid.spec

mkdir -p release/Mac release/Windows release/Installer release/ReleaseNotes
rm -rf "release/Mac/${APP_BUNDLE}"
rm -rf release/Mac/dmg
cp -R "dist/${APP_BUNDLE}" "release/Mac/${APP_BUNDLE}"

mkdir -p release/Mac/dmg
cp -R "release/Mac/${APP_BUNDLE}" "release/Mac/dmg/${APP_BUNDLE}"
ln -s /Applications release/Mac/dmg/Applications
cp RELEASE_NOTES.md release/ReleaseNotes/RELEASE_NOTES.md

if command -v hdiutil >/dev/null 2>&1; then
    rm -f "release/Mac/${DMG_NAME}"
    if ! hdiutil create \
        -volname "Lucid AI Studio" \
        -srcfolder release/Mac/dmg \
        -ov \
        -format UDZO \
        "release/Mac/${DMG_NAME}"; then
        echo "hdiutil create failed; falling back to hdiutil makehybrid"
        hdiutil makehybrid \
            -hfs \
            -hfs-volume-name "Lucid AI Studio" \
            -o "release/Mac/${DMG_NAME}" \
            release/Mac/dmg
    fi
fi

echo "macOS release ready: ${APP_RELEASE}"
echo "release/Mac/${APP_BUNDLE}"
echo "release/Mac/${DMG_NAME}"
