#!/bin/bash

set -e

echo "===== HGPT_AI_OS SMOKE TEST ====="

echo
echo "1. Test Runtime Status"
PYTHONPATH=src python3 -m hgpt_ai_os.cli.main status

echo
echo "2. Test Maintenance Agent"
PYTHONPATH=src python3 -m hgpt_ai_os.cli.main maintenance run

echo
echo "3. Test Task Create"
PYTHONPATH=src python3 -m hgpt_ai_os.cli.main task create "SMOKE TEST - HGPT_AI_OS"

echo
echo "4. Test Task List"
PYTHONPATH=src python3 -m hgpt_ai_os.cli.main task list

echo
echo "===== SMOKE TEST PASSED ====="
