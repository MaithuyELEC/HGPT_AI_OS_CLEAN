#!/bin/bash

set -e

PYTHON_BIN="python3"

if [ -x ".venv/bin/python" ]; then
    PYTHON_BIN=".venv/bin/python"
fi

echo "===== HGPT_AI_OS SMOKE TEST ====="

echo
echo "1. Test CLI Help"
PYTHONPATH=src "$PYTHON_BIN" -m hgpt_ai_os.cli.main --help

echo
echo "2. Test Production Generation"
PYTHONPATH=src "$PYTHON_BIN" -m hgpt_ai_os.cli.main production --topic "SMOKE TEST - HGPT_AI_OS"

echo
echo "3. Test GUI Import"
PYTHONPATH=src "$PYTHON_BIN" - <<'PY'
from hgpt_ai_os.core.production_result import ProductionResult
from hgpt_ai_os.gui.app import MainWindow
from hgpt_ai_os.gui.production_service import ProductionService
from hgpt_ai_os.gui.worker import ProductionWorker

assert MainWindow is not None
assert ProductionService is not None
assert ProductionWorker is not None
assert ProductionResult is not None

print("GUI import PASS")
PY

echo
echo "===== SMOKE TEST PASSED ====="
