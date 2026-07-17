# Lucid AI Studio v1.0.0 RC2 Release Notes

Lucid AI Studio v1.0.0 RC2 is the final packaging candidate for production desktop distribution.

## Scope

- No new product features.
- Runtime resources bundled for release: knowledge, templates, planner, assets, config, outputs.
- macOS one-command build creates `release/Mac/Lucid AI Studio.app` and `release/Mac/Lucid-AI-Studio-v1.0.0.dmg`.
- Windows one-command build creates `dist/LUCID/LUCID.exe` and `release/Installer/Lucid-AI-Studio-Setup-v1.0.0.exe`.
- Inno Setup builds `release/Installer/Lucid-AI-Studio-Setup-v1.0.0.exe` when detected.
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
