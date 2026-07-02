# Lucid Auto v1.0.0 RC14

> AI Production Operating System for Steel Fabrication.

---

# Overview

Lucid Auto là hệ thống AI Production được phát triển để tự động hóa quá trình tạo nội dung kỹ thuật, xây dựng Knowledge Base và tiến tới Digital Factory cho HGPT Steel.

---

# Features

- AI Content Generation
- Knowledge Engine
- Production CLI
- DOCX Export
- Marketing Automation
- Steel Knowledge Base
- QA/QC Knowledge
- SOP Generation (Roadmap)
- AI Agents (Roadmap)

---

# Project Structure

```text
HGPT_AI_OS_CLEAN/
├── src/
├── knowledge/
├── outputs/
├── templates/
├── planner/
├── assets/
├── installer/
├── release/
├── docs/
└── README.md
```

---

# Requirements

- Python 3.12+
- macOS / Windows / Linux
- Git

---

# Installation

```bash
git clone https://github.com/MaithuyELEC/HGPT_AI_OS_CLEAN.git

cd HGPT_AI_OS_CLEAN

python -m venv .venv

source .venv/bin/activate
```

---

# Quick Start

```bash
export PYTHONPATH=src

python -m hgpt_ai_os.production
```

---

# Release Build

macOS:

```bash
./build_mac.sh
```

Windows:

```cmd
build_windows.bat
```

Release artifacts are staged under `release/Mac/` and `release/Windows/`.

Packaging also prepares:

```text
release/
├── Mac/
│   ├── LUCID.app
│   └── LUCID-v1.0.0.dmg
├── Windows/
│   ├── LUCID.exe
│   └── LUCID/
├── Installer/
└── ReleaseNotes/
```

PyInstaller bundles `knowledge/`, `templates/`, `planner/`, `assets/`, `config/`, and `outputs/`.
Installer metadata and build artifact names read the release from `src/hgpt_ai_os/version.py`.

---

# Example

```text
Topic:
Sai khe hở Fit-up trước khi hàn
```

Output

```
outputs/
└── marketing/
    └── Day019/
```

---

# Roadmap

✅ Lucid Auto v1.0.0 RC14

✅ Installer packaging assets

⬜ Knowledge Engine v2

⬜ SOP Generator

⬜ AI Agents

⬜ Digital Factory

---

# Version

Current Release

```
v1.0.0 RC14
```

---

# Author

MaithuyELEC

HGPT Steel

---

# License

See LICENSE.
