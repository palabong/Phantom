#!/usr/bin/env bash
# phantom_cloud session bootstrap.
# Additive only. Does not touch phantom_cloud.py, Dockerfile, fly.toml, requirements.txt.
set -euo pipefail

GROK="/workspace/artifacts/.grok"
PROD="/workspace/artifacts/phantom_cloud"
ROOT="/workspace/artifacts"
VENV="/tmp/phantom_venv"
L0="$GROK/AGENTS.md"
L1="$GROK/project_memory"
L2="$PROD/README.md"
L2ARCH="$GROK/phantom_cloud_architecture.md"

echo "=== phantom_cloud cold-start bootstrap ==="
echo "time: $(date -u +%Y-%m-%dT%H:%M:%SZ)"

if [[ ! -d "$PROD" ]]; then
  echo "[FAIL] working root missing: $PROD"
  exit 1
fi
cd "$PROD"
echo "[OK] cwd: $PWD"

echo
echo "=== ingest layers ==="
for f in "$L0" "$L1" "$L2" "$L2ARCH"; do
  if [[ -f "$f" ]]; then
    echo "[OK] readable: $f ($(wc -c < "$f") bytes)"
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
echo "=== production evidence ==="
for f in \
  "$PROD/reports/SMOKE.md" \
  "$PROD/runs/prod_postdeploy_20260924T153949Z/SMOKE.md" \
  "$PROD/runs/prod_postdeploy_/stealth_evaluation.md" \
  "$PROD/.env.example" \
  "$PROD/.gitignore"
do
  if [[ -f "$f" ]]; then
    echo "[OK] readable: $f ($(wc -c < "$f") bytes)"
  else
    echo "[MISS] $f"
  fi
done
if [[ -f "$PROD/reports/CHANGELOG_LOCAL.md" ]]; then
  echo "[NOTE] CHANGELOG_LOCAL.md present — header 'not yet deployed' is superseded by later smoke archives"
fi

echo
echo "=== protected files (read-only unless user names the path) ==="
for f in phantom_cloud.py Dockerfile fly.toml requirements.txt; do
  if [[ -f "$PROD/$f" ]]; then
    echo "[OK] present: $f"
  else
    echo "[MISS] $f"
  fi
done

echo
echo "=== idle process hygiene ==="
CLEANED=0
PIDS=$(pgrep -f 'phantom_cloud.py|Xvfb|google-chrome|chromedriver|chromium' 2>/dev/null || true)
if [[ -z "$PIDS" ]]; then
  echo "[OK] no idle Chrome / Xvfb / local engine processes"
else
  for pid in $PIDS; do
    cmd=$(ps -o args= -p "$pid" 2>/dev/null || true)
    case "$cmd" in
      *init-session.sh*|*"pgrep -f"*) continue ;;
    esac
    case "$cmd" in
      *phantom_cloud.py*|*Xvfb*|*google-chrome*|*chromium*)
        echo "[KILL] pid=$pid $cmd"
        kill "$pid" 2>/dev/null || true
        CLEANED=1
        ;;
    esac
  done
  if [[ "$CLEANED" -eq 0 ]]; then
    echo "[OK] no idle Chrome / Xvfb / local engine processes"
  fi
fi

echo
echo "=== local venv /tmp/phantom_venv ==="
if [[ -x "$VENV/bin/python" ]]; then
  echo "[OK] venv python: $("$VENV/bin/python" --version 2>&1)"
  "$VENV/bin/python" -c "import nodriver,starlette,uvicorn" 2>/dev/null \
    && echo "[OK] core imports present" \
    || echo "[WARN] core imports missing — pip install -r requirements.txt when testing locally"
else
  echo "[INFO] venv absent. Attempting $VENV (artifacts FS cannot hold venv symlinks)."
  if python3 -m venv "$VENV" >/tmp/phantom_venv_bootstrap.log 2>&1; then
    "$VENV/bin/pip" install --upgrade pip >>/tmp/phantom_venv_bootstrap.log 2>&1 || true
    if [[ -f "$PROD/requirements.txt" ]]; then
      "$VENV/bin/pip" install -r "$PROD/requirements.txt" >>/tmp/phantom_venv_bootstrap.log 2>&1 \
        && echo "[OK] requirements installed" \
        || echo "[WARN] pip install failed — see /tmp/phantom_venv_bootstrap.log"
    fi
  else
    echo "[WARN] python3 -m venv failed (ensurepip / python3-venv missing in this sandbox)."
    echo "[WARN] local engine tests require a host with python3-venv. Production path is unaffected."
    rm -rf "$VENV" 2>/dev/null || true
  fi
fi

echo
echo "=== system packages (best-effort probe) ==="
if command -v google-chrome >/dev/null 2>&1; then
  echo "[OK] google-chrome"
elif command -v google-chrome-stable >/dev/null 2>&1; then
  echo "[OK] google-chrome-stable"
else
  echo "[WARN] chrome binary not on PATH"
fi
if command -v Xvfb >/dev/null 2>&1; then echo "[OK] Xvfb"; else echo "[WARN] Xvfb not on PATH"; fi
if command -v pkill >/dev/null 2>&1; then echo "[OK] pkill"; else echo "[WARN] pkill not on PATH"; fi

echo
echo "=== consult archive ==="
CONSULT="/Users/daniele_palagi/Desktop/phantom_cloud 2/grok/archive/20261008/consult"
if [[ -d "$CONSULT" ]]; then
  echo "[OK] consult set present: $CONSULT (not live CLI inputs; not L1)"
else
  echo "[INFO] no 20261008 consult archive"
fi
if [[ -f "$GROK/project_memory.md" ]]; then
  echo "[WARN] project_memory.md twin present — canonical L1 is project_memory"
fi

echo
echo "=== production target ==="
echo "app:      phantom-cloud-engine"
echo "region:   fra"
echo "hostname: https://phantom-cloud-engine.fly.dev"
echo "sse:      https://phantom-cloud-engine.fly.dev/sse/?token=<key>"
echo "messages: https://phantom-cloud-engine.fly.dev/messages/t/<token>"
echo "tools:    navigate, get_snapshot (html|ax), click, type, evaluate, wait"
echo "smoke:    runs/prod_postdeploy_20260924T153949Z"
echo "stealth:  runs/prod_postdeploy_/stealth_evaluation.md"
echo "drive:    1msmuBIu_28tNkjBxhKQ6S-x9DzfZjpO5"
echo "l0:       grok/AGENTS.md"
echo "next:     phantom-cloud-hygiene (do not auto-run)"

echo
echo "=== bootstrap complete ==="
echo "Next: emit readiness brief, then wait for the first user task."
