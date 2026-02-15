#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

echo "== OpenClaw Sentinel Demo =="
echo "Repo: $ROOT_DIR"

echo
echo "[1/5] Install"
SKIP_PIP_UPGRADE="${SKIP_PIP_UPGRADE:-1}" ./scripts/install.sh

# shellcheck disable=SC1091
source "$ROOT_DIR/.venv/bin/activate"

if command -v openclaw-onboarding >/dev/null 2>&1; then
  ONBOARD_CMD=(openclaw-onboarding)
else
  ONBOARD_CMD=(python3 -m openclaw_sentinel.onboarding)
fi

if command -v openclaw-sentinel >/dev/null 2>&1; then
  SENTINEL_CMD=(openclaw-sentinel)
else
  SENTINEL_CMD=(python3 -m openclaw_sentinel)
fi

echo
echo "[2/5] Onboarding (non-interactive)"
PYTHONPATH=src "${ONBOARD_CMD[@]}" \
  --non-interactive \
  --mode demo \
  --tenant-id demo-tenant \
  --autonomy-level L1 \
  --max-risk-score 2.8 \
  --output "$ROOT_DIR/.env.demo" \
  --overwrite

echo
echo "Generated .env.demo preview:"
sed -n '1,30p' "$ROOT_DIR/.env.demo"

echo
echo "[3/5] Run tests (quality proof)"
PYTHONPATH=src python3 -m unittest discover -s tests -v

echo
echo "[4/5] Autonomous run (demo mode, 2 cycles)"
PYTHONPATH=src "${SENTINEL_CMD[@]}" --mode demo --cycles 2 --debug --log-file "$ROOT_DIR/openclaw-demo.log"

echo
echo "[5/5] Show outcomes"
echo "Log file: $ROOT_DIR/openclaw-demo.log"
tail -n 20 "$ROOT_DIR/openclaw-demo.log" || true

echo
echo "Demo complete."
echo "Key outcomes to highlight:"
echo "- Installer + onboarding completed"
echo "- Full test suite passed"
echo "- Autonomous cycles executed with metrics output"
echo "- Debug logs captured for traceability"
