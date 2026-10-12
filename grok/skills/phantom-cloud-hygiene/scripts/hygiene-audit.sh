#!/usr/bin/env bash
# Read-only hygiene inventory. Does not kill, move, or delete.
set -euo pipefail

GROK="/workspace/artifacts/.grok"
PROD="/workspace/artifacts/phantom_cloud"
ROOT="/workspace/artifacts"
SKILLS="/root/.grok/server-skills"
VENV="/tmp/phantom_venv"
L0="$GROK/AGENTS.md"
L1="$GROK/project_memory"
L2="$PROD/README.md"
L2ARCH="$GROK/phantom_cloud_architecture.md"

echo "=== phantom_cloud hygiene audit (read-only) ==="
echo "time: $(date -u +%Y-%m-%dT%H:%M:%SZ)"

echo
echo "=== canonical layers ==="
for f in "$L0" "$L1" "$L2" "$L2ARCH"; do
  if [[ -f "$f" ]]; then
    echo "[OK] $f ($(wc -c < "$f") bytes)"
  else
    echo "[MISS] $f"
  fi
done

if [[ -f "$L0" ]]; then
  rev=$(grep -m1 '^INGEST REVISION:' "$L0" || true)
  ver=$(grep -m1 '^VERSION:' "$L0" || true)
  echo "[OK] ${rev:-INGEST REVISION missing}"
  echo "[OK] ${ver:-VERSION missing}"
else
  echo "[FAIL] canonical L0 missing"
fi

if [[ -f "$ROOT/AGENTS.md" ]]; then
  if grep -q '^INGEST REVISION:' "$ROOT/AGENTS.md"; then
    echo "[WARN] root artifacts/AGENTS.md contains INGEST REVISION — pointer should not be full L0"
  else
    echo "[OK] root artifacts/AGENTS.md is a pointer, not L0"
  fi
fi

if [[ -d "$PROD/.grok" ]]; then
  echo "[WARN] $PROD/.grok exists — not canonical; do not treat as L0"
else
  echo "[OK] no .grok/"
fi

echo
echo "=== L1 twins ==="
if [[ -f "$GROK/project_memory.md" ]]; then
  echo "[FIND] P1-DUP $GROK/project_memory.md (canonical is project_memory without .md)"
else
  echo "[OK] no project_memory.md twin"
fi

echo
echo "=== production evidence ==="
for f in \
  "$PROD/reports/SMOKE.md" \
  "$PROD/runs/prod_postdeploy_20260924T153949Z/SMOKE.md" \
  "$PROD/runs/prod_postdeploy_/stealth_evaluation.md"
do
  if [[ -f "$f" ]]; then
    echo "[OK] $f"
  else
    echo "[MISS] $f"
  fi
done
if [[ -f "$PROD/reports/CHANGELOG_LOCAL.md" ]]; then
  echo "[INFO] CHANGELOG_LOCAL.md present — 'not yet deployed' header is superseded"
fi

echo
echo "=== protected production files ==="
for f in phantom_cloud.py Dockerfile fly.toml requirements.txt; do
  if [[ -f "$PROD/$f" ]]; then
    echo "[OK] $f"
  else
    echo "[MISS] $f"
  fi
done

echo
echo "=== select artifacts vs INGEST REVISION ==="
if [[ -f "$L0" ]]; then
  ingest_raw=$(grep -m1 '^INGEST REVISION:' "$L0" | awk '{print $2}' || true)
  ingest_epoch=$(date -u -d "$ingest_raw" +%s 2>/dev/null || echo 0)
  while IFS= read -r f; do
    [[ -f "$f" ]] || continue
    mt=$(stat -c '%Y' "$f")
    if [[ "$ingest_epoch" -gt 0 && "$mt" -gt "$ingest_epoch" ]]; then
      echo "[FIND] P3-INGEST newer than INGEST REVISION: $f ($(date -u -d "@$mt" +%Y-%m-%dT%H:%M:%SZ))"
    else
      echo "[OK] $(basename "$f") not newer than ingest"
    fi
  done <<EOF
$GROK/project_memory
$GROK/phantom_cloud_architecture.md
$PROD/README.md
$PROD/reports/SMOKE.md
$PROD/commercial/PILOT_OFFER.md
$PROD/commercial/ROE_AND_SCOPE.md
$PROD/commercial/ONBOARDING_CHECKLIST.md
$PROD/commercial/PRICING_FRAME.md
$PROD/.env.example
EOF
fi

echo
echo "=== agent-owned files (header stamp) ==="
shopt -s nullglob
for f in "$GROK"/*; do
  [[ -f "$f" ]] || continue
  base=$(basename "$f")
  case "$base" in
    AGENTS.md|project_memory|phantom_cloud_architecture.md) continue ;;
  esac
  if grep -q '^PROJECT: phantom_cloud' "$f" 2>/dev/null && grep -q '^UPDATED:' "$f" 2>/dev/null; then
    echo "[OK] stamp $base"
  else
    echo "[FIND] P2-STAMP missing header stamp: $f"
  fi
done
shopt -u nullglob

echo
echo "=== skill path drift ==="
# Flag only skills that still instruct the agent to *use* the old L0 path.
# Mentions that negate it (hygiene doctrine) are not drift.
hits=$(grep -R -n '.grok' "$SKILLS"/phantom-cloud-* \
  --exclude-dir=phantom-cloud-hygiene 2>/dev/null || true)
if [[ -n "$hits" ]]; then
  echo "[FIND] P1-CANON skills still name .grok as L0"
  echo "$hits" | head -20
else
  echo "[OK] no skill path to .grok"
fi

echo
echo "=== idle processes ==="
PIDS=$(pgrep -f 'phantom_cloud.py|Xvfb|google-chrome|chromedriver|chromium' 2>/dev/null || true)
if [[ -z "$PIDS" ]]; then
  echo "[OK] no idle Chrome / Xvfb / local engine"
else
  for pid in $PIDS; do
    cmd=$(ps -o args= -p "$pid" 2>/dev/null || true)
    echo "[FIND] P0-RUNTIME pid=$pid $cmd"
  done
fi

echo
echo "=== local venv ==="
if [[ -x "$VENV/bin/python" ]]; then
  echo "[OK] $VENV $($VENV/bin/python --version 2>&1)"
else
  echo "[INFO] $VENV absent — sandbox gap, not a production defect"
fi
if command -v google-chrome >/dev/null 2>&1 || command -v google-chrome-stable >/dev/null 2>&1; then
  echo "[OK] chrome binary on PATH"
else
  echo "[INFO] chrome binary not on PATH"
fi
if command -v Xvfb >/dev/null 2>&1; then echo "[OK] Xvfb"; else echo "[INFO] Xvfb not on PATH"; fi

echo
echo "=== audit complete (no changes made) ==="
echo "Next: classify findings, emit audit brief, wait for confirmation."
