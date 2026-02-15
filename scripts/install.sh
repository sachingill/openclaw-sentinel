#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PYTHON_BIN="${PYTHON_BIN:-python3}"
VENV_DIR="${VENV_DIR:-$ROOT_DIR/.venv}"

if ! command -v "$PYTHON_BIN" >/dev/null 2>&1; then
  echo "error: $PYTHON_BIN not found" >&2
  exit 1
fi

PY_VERSION="$($PYTHON_BIN -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')"
REQ_MAJOR=3
REQ_MINOR=10
MAJOR="${PY_VERSION%%.*}"
MINOR="${PY_VERSION##*.}"
if [ "$MAJOR" -lt "$REQ_MAJOR" ] || { [ "$MAJOR" -eq "$REQ_MAJOR" ] && [ "$MINOR" -lt "$REQ_MINOR" ]; }; then
  echo "error: Python >= 3.10 required (found $PY_VERSION)" >&2
  exit 1
fi

if [ ! -d "$VENV_DIR" ]; then
  "$PYTHON_BIN" -m venv "$VENV_DIR"
fi

# shellcheck disable=SC1090
source "$VENV_DIR/bin/activate"

if [ "${SKIP_PIP_UPGRADE:-0}" = "1" ]; then
  echo "Skipping pip/setuptools/wheel upgrade (SKIP_PIP_UPGRADE=1)."
else
  if ! python -m pip install --upgrade pip setuptools wheel; then
    echo "warning: pip tooling upgrade failed; continuing with existing tooling." >&2
  fi
fi

INSTALLED_EDITABLE=0
if python -m pip install --no-build-isolation -e "$ROOT_DIR"; then
  INSTALLED_EDITABLE=1
else
  echo "warning: editable package install failed; using module-based commands as fallback." >&2
fi

echo
cat <<MSG
OpenClaw Sentinel installation complete.

Next steps:
1. Activate env: source "$VENV_DIR/bin/activate"
MSG

if [ "$INSTALLED_EDITABLE" -eq 1 ]; then
  cat <<MSG
2. Run onboarding: openclaw-onboarding --output "$ROOT_DIR/.env"
3. Demo run: openclaw-sentinel --mode demo --cycles 1
MSG
else
  cat <<MSG
2. Run onboarding: PYTHONPATH=src python3 -m openclaw_sentinel.onboarding --output "$ROOT_DIR/.env"
3. Demo run: PYTHONPATH=src python3 -m openclaw_sentinel --mode demo --cycles 1
MSG
fi
