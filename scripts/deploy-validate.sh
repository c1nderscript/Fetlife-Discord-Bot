#!/usr/bin/env bash
set -euo pipefail

if [[ ${EUID:-$(id -u)} -eq 0 ]]; then
  echo "Refusing to run deploy validation as root" >&2
  exit 1
fi

confirm=false
if [[ "${1:-}" == "--confirm" ]]; then
  confirm=true
  shift
fi

dry_run=true
$confirm && dry_run=false

run() {
  if $dry_run; then
    echo "[dry-run] $*"
  else
    "$@"
  fi
}

missing=false
for var in SESSION_SECRET ADAPTER_AUTH_TOKEN ADMIN_IDS DATABASE_URL; do
  if [[ -z "${!var:-}" ]]; then
    echo "Missing required env var: $var" >&2
    missing=true
  fi
done
if $missing; then
  exit 1
fi

run psql "$DATABASE_URL" -c 'select 1' >/dev/null

cert_path=${TLS_CERT_PATH:-certs/tls.crt}
if [[ ! -f "$cert_path" ]]; then
  echo "TLS certificate not found at $cert_path" >&2
  exit 1
fi

echo "deploy validation passed"
