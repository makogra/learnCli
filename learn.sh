#!/bin/bash

SCRIPT_PATH="$(readlink -f "$0")"
SCRIPT_DIR="$(dirname "$SCRIPT_PATH")"
VENV_DIR="$SCRIPT_DIR/venv"

source "$VENV_DIR/bin/activate"
python3 $SCRIPT_DIR/main.py "$@"