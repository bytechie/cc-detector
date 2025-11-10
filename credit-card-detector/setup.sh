#!/usr/bin/env bash
set -euo pipefail

# Minimal onboarding script
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="$ROOT_DIR/.venv"

echo "Setting up virtualenv in $VENV_DIR"
python3 -m venv "$VENV_DIR"
source "$VENV_DIR/bin/activate"

if [ -f "$ROOT_DIR/requirements.txt" ]; then
    pip install --upgrade pip
    pip install -r "$ROOT_DIR/requirements.txt"
else
    echo "No requirements.txt found — skipping pip install"
fi

# Create .env from example if not present
if [ -f "$ROOT_DIR/.env" ]; then
    echo ".env already exists"
else
    if [ -f "$ROOT_DIR/.env.example" ]; then
        cp "$ROOT_DIR/.env.example" "$ROOT_DIR/.env"
        echo "Created .env from .env.example"
    fi
fi

echo "Setup complete. Activate the venv with: source $VENV_DIR/bin/activate"
