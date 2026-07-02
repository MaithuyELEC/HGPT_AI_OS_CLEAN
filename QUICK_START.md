# Quick Start

## 1. Clone Repository

```bash
git clone https://github.com/MaithuyELEC/HGPT_AI_OS_CLEAN.git

cd HGPT_AI_OS_CLEAN
```

---

## 2. Create Virtual Environment

```bash
python3 -m venv .venv
```

---

## 3. Activate

### macOS / Linux

```bash
source .venv/bin/activate
```

### Windows

```cmd
.venv\Scripts\activate
```

---

## 4. Install Dependencies

```bash
pip install -r requirements.txt
```

---

## 5. Set Python Path

### macOS / Linux

```bash
export PYTHONPATH=src
```

### Windows

```cmd
set PYTHONPATH=src
```

---

## 6. Run Production

```bash
python -m hgpt_ai_os.production --topic "Sai khe hở Fit-up trước khi hàn"
```

---

## Expected Output

```text
STATUS : PRODUCTION SUCCESS
```

---

## Output Directory

```text
outputs/
└── marketing/
```

---

## Next

* Read INSTALL.md for complete installation.
* Read README.md for project overview.
* Run `./build_mac.sh` or `build_windows.bat` for one-command release packaging.

## Packaging Output

```text
release/
├── Mac/
├── Windows/
├── Installer/
└── ReleaseNotes/
```
