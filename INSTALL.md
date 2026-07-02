# LUCID AUTO Installation

## Requirements

- Python 3.12+
- Git
- PyInstaller
- macOS or Windows

## Source Install

```bash
git clone https://github.com/MaithuyELEC/HGPT_AI_OS_CLEAN.git
cd HGPT_AI_OS_CLEAN
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
export PYTHONPATH=src
python -m hgpt_ai_os.production --topic "Smoke test"
```

Windows:

```cmd
git clone https://github.com/MaithuyELEC/HGPT_AI_OS_CLEAN.git
cd HGPT_AI_OS_CLEAN
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
set PYTHONPATH=src
python -m hgpt_ai_os.production --topic "Smoke test"
```

## macOS Package

```bash
./build_mac.sh
```

Output:

```text
release/Mac/LUCID.app
release/Mac/LUCID-v1.0.0.dmg
```

## Windows Package

```cmd
build_windows.bat
```

Output:

```text
release\Windows\LUCID.exe
release\Windows\LUCID\
installer\LUCID.iss
release\Installer\LUCID Setup.exe
```

If Inno Setup is not detected, `build_windows.bat` still writes `installer\LUCID.iss`.

## Runtime Resources

PyInstaller bundles:

```text
knowledge/
templates/
planner/
assets/
config/
outputs/
```

## Version Source

Release scripts and installer metadata read `src/hgpt_ai_os/version.py`.
