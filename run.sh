#!/usr/bin/env bash
set -euo pipefail

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="$HOME/.jarvis-venv"

# shellcheck disable=SC1090
source "$VENV_DIR/bin/activate"
python "$PROJECT_DIR/main.py"
