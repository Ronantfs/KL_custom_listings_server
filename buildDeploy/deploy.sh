#!/bin/bash
set -euo pipefail

# Resolve dirs
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
VENV_DIR="$PROJECT_DIR/.venv"

if [[ ! -f "$VENV_DIR/bin/activate" ]]; then
  echo "ERROR: venv not found at $VENV_DIR"
  echo "Create it with: python3 -m venv .venv && .venv/bin/pip install boto3"
  exit 1
fi

source "$VENV_DIR/bin/activate"
python "$SCRIPT_DIR/deploy_lambda.py" "$@"
