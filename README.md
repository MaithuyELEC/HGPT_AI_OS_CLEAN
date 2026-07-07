# LUCID PLATFORM

> AI Production Operating System for Steel Fabrication.

---

# Overview

LUCID PLATFORM is the long-term production software foundation for HGPT Steel AI
operations. It evolves the existing LUCID AUTO production system into a universal
runtime for providers, knowledge, agents, plugins, marketplace architecture,
enterprise controls, and Digital Factory workflows.

The current production path remains backward compatible while platform
capabilities are delivered one sprint at a time.

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

# Platform Documentation

- [Architecture](docs/architecture.md)
- [Platform contracts](docs/contracts.md)
- [Roadmap](docs/roadmap.md)
- [Migration plan from LUCID AUTO](docs/migration_lucid_auto_to_platform.md)

---

# Roadmap

✅ Sprint 01 Universal Runtime

✅ Sprint 02 Platform Contracts

⬜ Sprint 03 Universal Knowledge

⬜ Sprint 04 Agent System

⬜ Sprint 05 Plugin SDK

⬜ Sprint 06 Marketplace Architecture

⬜ Sprint 07 Enterprise Architecture

⬜ Sprint 08 Digital Factory Architecture

---

# Version

Current Release

```
LUCID PLATFORM Sprint 01 / v1.0.0 RC14 compatibility line
```

---

# Author

MaithuyELEC

HGPT Steel

---

# License

See LICENSE.
