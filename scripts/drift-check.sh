#!/usr/bin/env bash
set -euo pipefail

# Compare deployed config with repository version using SHA256.
# Default: repo config.yaml vs /etc/fetlife/config.yaml
# Pass alternate deployed path as argument. Use --confirm to restore drift.

DRY_RUN=1
if [[ "${1:-}" == "--confirm" ]]; then
  DRY_RUN=0
  shift
fi

REPO_CONFIG="config.yaml"
DEPLOY_CONFIG="${1:-/etc/fetlife/config.yaml}"

if [[ "${DEPLOY_CONFIG}" != /* ]]; then
  echo "Deployed config path must be absolute" >&2
  exit 1
fi

if [[ ! -f "$REPO_CONFIG" ]]; then
  echo "Repository config '$REPO_CONFIG' missing" >&2
  exit 1
fi

if [[ ! -f "$DEPLOY_CONFIG" ]]; then
  echo "Deployed config '$DEPLOY_CONFIG' missing" >&2
  exit 1
fi

repo_sum=$(sha256sum "$REPO_CONFIG" | awk '{print $1}')
deploy_sum=$(sha256sum "$DEPLOY_CONFIG" | awk '{print $1}')

if [[ "$repo_sum" != "$deploy_sum" ]]; then
  echo "Config drift detected: repository=$repo_sum deployed=$deploy_sum" >&2
  if [[ $DRY_RUN -eq 0 ]]; then
    cp "$REPO_CONFIG" "$DEPLOY_CONFIG"
    echo "Deployed config restored from repository copy."
  else
    echo "Run with --confirm to restore deployed config." >&2
    exit 1
  fi
else
  echo "No config drift detected."
fi
