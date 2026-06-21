#!/bin/bash
set -e

echo "===== LUCID DAY11 E2E TEST ====="

PYTHONPATH=src python3 -m hgpt_ai_os.cli.main lucid day11
PYTHONPATH=src python3 -m hgpt_ai_os.cli.main lucid status
PYTHONPATH=src python3 -m hgpt_ai_os.cli.main lucid approve day11
PYTHONPATH=src python3 -m hgpt_ai_os.cli.main lucid ready day11
PYTHONPATH=src python3 -m hgpt_ai_os.cli.main lucid status

echo
echo "Output folder:"
ls -la outputs/marketing/day11

echo
echo "Ready folder:"
ls -la outputs/marketing/day11/READY_TO_POST

echo
echo "===== LUCID DAY11 E2E TEST PASSED ====="
