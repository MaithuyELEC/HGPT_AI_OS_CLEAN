from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
VERSION_FILE = ROOT / "src" / "hgpt_ai_os" / "version.py"
INSTALLER = ROOT / "installer" / "LUCID.iss"


def _read_version() -> dict[str, str]:
    values: dict[str, str] = {}
    exec(VERSION_FILE.read_text(), values)
    return values


def main() -> int:
    values = _read_version()
    app_version = values["APP_VERSION"]
    app_release = values["APP_RELEASE"]
    INSTALLER.parent.mkdir(exist_ok=True)
    INSTALLER.write_text(
        f"""#define MyAppName "LUCID AUTO"
#define MyAppVersion "{app_version}"
#define MyAppRelease "{app_release}"
#define MyAppPublisher "HGPT Steel"
#define MyAppExeName "LUCID.exe"

[Setup]
AppId={{{{0A13B87E-05F2-4E57-9F0A-7B3E750C87D4}}}}
AppName={{#MyAppName}}
AppVersion={{#MyAppVersion}}
AppPublisher={{#MyAppPublisher}}
DefaultDirName={{autopf}}\\LUCID AUTO
DefaultGroupName=LUCID AUTO
DisableProgramGroupPage=yes
OutputDir=..\\release\\Installer
OutputBaseFilename=LUCID Setup
Compression=lzma
SolidCompression=yes
WizardStyle=modern
SetupIconFile=..\\assets\\LUCID.ico

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{{cm:CreateDesktopIcon}}"; GroupDescription: "{{cm:AdditionalIcons}}"

[Files]
Source: "..\\release\\Windows\\LUCID\\*"; DestDir: "{{app}}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{{group}}\\LUCID AUTO"; Filename: "{{app}}\\{{#MyAppExeName}}"
Name: "{{autodesktop}}\\LUCID AUTO"; Filename: "{{app}}\\{{#MyAppExeName}}"; Tasks: desktopicon

[Run]
Filename: "{{app}}\\{{#MyAppExeName}}"; Description: "{{cm:LaunchProgram,LUCID AUTO}}"; Flags: nowait postinstall skipifsilent
""",
        encoding="utf-8",
    )
    print(f"Wrote {INSTALLER.relative_to(ROOT)} for {app_release}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
