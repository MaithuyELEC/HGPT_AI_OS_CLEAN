# LUCID AUTO v1.0.0 RC14 Release Notes

LUCID AUTO v1.0.0 RC14 is the final packaging candidate for production desktop distribution.

## Scope

- No new product features.
- Runtime resources bundled for PyInstaller: knowledge, templates, planner, assets, config, outputs.
- macOS one-command build creates `release/Mac/LUCID.app` and `release/Mac/LUCID-v1.0.0.dmg`.
- Windows one-command build creates `release/Windows/LUCID.exe`, `release/Windows/LUCID`, and `installer/LUCID.iss`.
- Inno Setup builds `release/Installer/LUCID Setup.exe` when detected.
- Release staging folders prepared for macOS, Windows, installer assets, and release notes.
- Application version centralized in `src/hgpt_ai_os/version.py`.

## Verification Checklist

- Compile PASS
- Smoke PASS
- Packaging PASS
- macOS PASS
- Windows PASS
- Desktop Launch PASS
- Generate PASS
- Knowledge PASS
- DOCX Export PASS
- Output Folder PASS
- Mock Provider PASS
- One-command build PASS
