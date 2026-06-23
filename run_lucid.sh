#!/bin/bash

source .venv/bin/activate

export PYTHONPATH=src

python3 -m hgpt_ai_os.cli.main lucid run
