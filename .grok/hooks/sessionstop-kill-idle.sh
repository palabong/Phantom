#!/bin/sh
# SessionEnd leftover killer for this phantom_cloud checkout.
# Grok event name is SessionEnd (there is no SessionStop). This script is not
# registered in .grok/config.toml (project config does not load [[hooks]]).
# To attach: trust the folder (/hooks-trust or grok --trust), then add a
# project hook JSON or a user [[hooks.SessionEnd]] command pointing here.
# Safe no-op if nothing matches.

set -u

ROOT="${GROK_WORKSPACE_ROOT:-}"
CWD="${PWD:-}"
case "${ROOT} ${CWD}" in
  *phantom_cloud*) ;;
  *) exit 0 ;;
esac

# Local engine started as: python phantom_cloud.py (this tree's module name).
pkill -f '[p]ython[^ ]* phantom_cloud\.py' >/dev/null 2>&1 || true

# Dockerfile / README Xvfb geometry for this engine only.
pkill -f '[X]vfb .*1920x1080x24' >/dev/null 2>&1 || true

# Linux image Chrome launched by nodriver for this engine (not macOS Chrome.app).
pkill -f '[g]oogle-chrome-stable .*--user-data-dir' >/dev/null 2>&1 || true

exit 0
