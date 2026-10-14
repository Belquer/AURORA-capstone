#!/bin/bash
# Double-click to start the AURORA live reader (iPhone via Continuity Camera, or any webcam).
cd "$(dirname "$0")"
if ! command -v python3 >/dev/null; then
  echo "Python 3 is missing. Install it from https://www.python.org/downloads/ and double-click again."; read -n1; exit 1
fi
if [ ! -x .venv/bin/python ]; then
  echo "First run: setting up (about a minute)..."
  python3 -m venv .venv && ./.venv/bin/pip install -q --upgrade pip && ./.venv/bin/pip install -q -r requirements.txt || { echo "Setup failed"; read -n1; exit 1; }
fi
./.venv/bin/python iphone_reader.py "$@"
