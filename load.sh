#!/bin/bash

set -euo pipefail

INPUT_FILE="$1"
ARCHIVE_DIR="./archive"
VENV_DIR="./venv"
PYTHON_SCRIPT="./challenge_loader.py"

# Activate virtual environment
source "$VENV_DIR/bin/activate"

# Run loader
if python3 "$PYTHON_SCRIPT" "$INPUT_FILE"; then
    echo "Load succeeded. Archiving file..."
    mv "$INPUT_FILE" "$ARCHIVE_DIR/$(date +%F)_$(basename $INPUT_FILE)"
else
    echo "Load failed. File not archived."
    exit 1
fi