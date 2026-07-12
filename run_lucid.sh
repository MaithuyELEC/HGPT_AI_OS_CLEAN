#!/bin/bash

set -e

cd "$(dirname "$0")"

source .venv/bin/activate

export PYTHONPATH=src

echo "=================================="
echo " LUCID AUTO - Development Mode"
echo "=================================="

python3 -m hgpt_ai_os.gui.app
