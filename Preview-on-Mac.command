#!/bin/bash
# Double-click (or right-click → Open) for a local site preview on macOS.
set -e
cd "$(dirname "$0")"
if ! command -v python3 >/dev/null 2>&1; then
  echo "Python 3 is required. Install from https://www.python.org/downloads/ and reopen this file."
  read -r -p "Press Return to close..."
  exit 1
fi
python3 scripts/build.py --serve
