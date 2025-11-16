#!/usr/bin/env bash
set -euo pipefail

echo "[Jarvis] Starting installation..."

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="$HOME/.jarvis-venv"

echo "[Jarvis] Updating apt..."
sudo apt update

echo "[Jarvis] Installing system dependencies..."
sudo apt install -y \
  python3 python3-venv python3-pip \
  portaudio19-dev python3-pyaudio \
  espeak \
  git curl

echo "[Jarvis] Creating Python virtual environment at $VENV_DIR..."
if [ ! -d "$VENV_DIR" ]; then
  python3 -m venv "$VENV_DIR"
fi

echo "[Jarvis] Activating virtual environment and installing Python packages..."
# shellcheck disable=SC1090
source "$VENV_DIR/bin/activate"
pip install --upgrade pip
pip install -r "$PROJECT_DIR/requirements.txt"

echo "[Jarvis] Checking for Ollama..."
if ! command -v ollama >/dev/null 2>&1; then
  echo "[Jarvis] Installing Ollama..."
  curl -fsSL https://ollama.com/install.sh | sh
fi

echo "[Jarvis] Pulling LLM model (qwen3:1.7b)..."
# Adjust this if you change the model name in main.py
ollama pull qwen3:1.7b || true

echo
echo "[Jarvis] Installation complete ✅"
echo "To run Jarvis manually:"
echo "  source \"$VENV_DIR/bin/activate\""
echo "  python \"$PROJECT_DIR/main.py\""
echo
echo "Or just run:"
echo "  $PROJECT_DIR/run.sh"
