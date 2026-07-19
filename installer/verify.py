from __future__ import annotations

import plistlib
import platform
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
version_ns = {}
exec((ROOT / "src" / "hgpt_ai_os" / "version.py").read_text(), version_ns)
APP_VERSION = version_ns["APP_VERSION"].removeprefix("v")
APP_BUILD = version_ns["APP_BUILD"].removeprefix("RC")
MAC_DMG_ROOT = ROOT / "release" / "Mac" / "dmg"
MAC_APP = MAC_DMG_ROOT / "Lucid AI Studio.app"
ISS_PATH = ROOT / "installer" / "LUCID.iss"
WINDOWS_DIST = ROOT / "dist" / "LUCID"
WINDOWS_APP = WINDOWS_DIST / "LUCID.exe"
WINDOWS_INSTALLER_ROOT = ROOT / "release" / "Installer"
WINDOWS_QT_FILES = [
    "Qt6Core.dll",
    "Qt6Gui.dll",
    "Qt6Widgets.dll",
]
WINDOWS_QWINDOWS = "qwindows.dll"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(f"installer verification failed: {message}")


def verify_macos() -> None:
    apps_link = MAC_DMG_ROOT / "Applications"
    plist_path = MAC_APP / "Contents" / "Info.plist"

    require(apps_link.is_symlink(), "DMG staging is missing Applications shortcut")
    require(apps_link.readlink() == Path("/Applications"), "Applications shortcut must target /Applications")
    require(plist_path.is_file(), "macOS bundle is missing Info.plist")
    require((MAC_APP / "Contents" / "Resources" / "LUCID.icns").is_file(), "macOS bundle is missing LUCID.icns")
    require((MAC_APP / "Contents" / "MacOS" / "LUCID").is_file(), "macOS bundle is missing executable")

    with plist_path.open("rb") as plist_file:
        plist = plistlib.load(plist_file)

    expected = {
        "CFBundleDisplayName": "Lucid AI Studio",
        "CFBundleExecutable": "LUCID",
        "CFBundleIconFile": "LUCID.icns",
        "CFBundleIdentifier": "com.lucidauto.desktop",
        "CFBundleName": "Lucid AI Studio",
        "CFBundleShortVersionString": APP_VERSION,
        "CFBundleVersion": APP_BUILD,
        "LSApplicationCategoryType": "public.app-category.productivity",
    }
    for key, value in expected.items():
        require(plist.get(key) == value, f"Info.plist {key} must be {value!r}")


def verify_windows() -> None:
    if platform.system() != "Windows":
        print("SKIPPED: Windows packaging verification requires Windows")
        return

    require(ISS_PATH.is_file(), "missing Inno Setup script")
    text = ISS_PATH.read_text(encoding="utf-8")

    required_fragments = [
        'AppPublisher={#MyAppPublisher}',
        "AppVerName={#MyAppName} {#MyAppRelease}",
        "UninstallDisplayIcon={app}\\{#MyAppExeName}",
        "UninstallDisplayName={#MyAppName} {#MyAppRelease}",
        "VersionInfoVersion={#MyAppVersion}",
        "VersionInfoCompany={#MyAppPublisher}",
        "OutputBaseFilename=Lucid-AI-Studio-Setup-v{#MyAppVersion}",
        'Source: "..\\dist\\LUCID\\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs',
        'Name: "{group}\\Lucid AI Studio"; Filename: "{app}\\{#MyAppExeName}"',
        'Name: "{group}\\Uninstall Lucid AI Studio"; Filename: "{uninstallexe}"',
        'Name: "{autodesktop}\\Lucid AI Studio"; Filename: "{app}\\{#MyAppExeName}"; Tasks: desktopicon',
    ]
    for fragment in required_fragments:
        require(fragment in text, f"Inno Setup script missing {fragment}")

    require(WINDOWS_DIST.is_dir(), "PyInstaller dist output is missing")
    require(WINDOWS_APP.is_file(), "PyInstaller output is missing dist/LUCID/LUCID.exe")
    for qt_file in WINDOWS_QT_FILES:
        require(
            any(WINDOWS_DIST.rglob(qt_file)),
            f"PyInstaller output is missing bundled Qt runtime file: {qt_file}",
        )
    require(
        any(path.name == WINDOWS_QWINDOWS and path.parent.name == "platforms" for path in WINDOWS_DIST.rglob(WINDOWS_QWINDOWS)),
        "PyInstaller output is missing bundled Qt runtime file: platforms/qwindows.dll",
    )

    if any(WINDOWS_INSTALLER_ROOT.glob("*.exe")):
        require((WINDOWS_INSTALLER_ROOT / f"Lucid-AI-Studio-Setup-v{APP_VERSION}.exe").is_file(), "expected Windows installer output is missing")


def main() -> None:
    target = sys.argv[1].lower() if len(sys.argv) > 1 else "all"
    require(target in {"all", "macos", "windows"}, "usage: verify.py [all|macos|windows]")

    if target in {"all", "macos"}:
        verify_macos()
    if target in {"all", "windows"}:
        verify_windows()

    print(f"installer verification passed: {target}")


if __name__ == "__main__":
    main()
