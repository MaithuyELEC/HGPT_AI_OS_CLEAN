# Changelog

## v1.0.0 RC14

- Bundled PyInstaller runtime resources for `knowledge/`, `templates/`, `planner/`, `assets/`, config resources, and `outputs/`.
- Updated macOS packaging to stage `release/Mac/LUCID.app` and `release/Mac/LUCID-v1.0.0.dmg`.
- Updated Windows packaging to stage `release/Windows/LUCID.exe`, prepare installer payloads, and generate `installer/LUCID.iss`.
- Added optional Inno Setup output under `release/Installer/`.
- Kept release metadata sourced from `src/hgpt_ai_os/version.py`.

## v1.0.0 RC13

- Centralized application version in `src/hgpt_ai_os/version.py`.
- Updated PyInstaller resource bundling for `knowledge/`, `templates/`, `assets/`, `planner/`, and config resources.
- Added macOS one-command build script.
- Added Windows one-command build script.
- Added release staging folders for macOS and Windows.
- Added release checklist and release notes.
